"""
Views for AI operations (RAG query interface).
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.documents.models import Document
from .serializers import QuerySerializer, QueryResponseSerializer, DocumentStatusSerializer


class AIViewSet(viewsets.ViewSet):
    """ViewSet for AI operations."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def query(self, request):
        """Ask a question about user's documents (RAG or document search)."""
        serializer = QuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question = serializer.validated_data['question']
        history  = request.data.get('history', [])

        try:
            from apps.ai_engine.gemini import detect_query_intent

            # Detect intent using Gemini
            intent_result = detect_query_intent(question, history)
            intent        = intent_result.get('intent', 'answer_question')
            filters       = intent_result.get('filters', {})

            # ── Intent: list/find documents ──────────────────────
            if intent == 'list_documents':
                return self._handle_list_documents(request, question, filters)

            # ── Intent: answer question using RAG ────────────────
            else:
                return self._handle_rag_query(request, question, history)

        except Exception as e:
            return Response(
                {'error': f'Query failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def _handle_list_documents(self, request, question, filters):
        """Handle document search/list queries with Gemini-extracted filters."""
        from django.db.models import Q, Sum

        queryset = Document.objects.filter(
            user=request.user,
            is_deleted=False,
            status__in=['processed', 'ready']
        )

        # Apply filters from Gemini
        if filters.get('category'):
            queryset = queryset.filter(category=filters['category'])

        if filters.get('date_from'):
            queryset = queryset.filter(
                extracted_date__gte=filters['date_from']
            )

        if filters.get('date_to'):
            queryset = queryset.filter(
                extracted_date__lte=filters['date_to']
            )

        if filters.get('vendor'):
            queryset = queryset.filter(
                extracted_vendor__icontains=filters['vendor']
            )

        if filters.get('search_term'):
            term = filters['search_term']
            queryset = queryset.filter(
                Q(original_name__icontains=term) |
                Q(extracted_vendor__icontains=term) |
                Q(summary__icontains=term)
            )

        documents = queryset.order_by('-extracted_date', '-created_at')[:20]

        if not documents.exists():
            return Response({
                'answer':    "I couldn't find any documents matching your request.",
                'intent':    'list_documents',
                'documents': [],
                'sources':   [],
            }, status=status.HTTP_200_OK)

        # Build natural language summary
        count   = documents.count()
        cat_str = filters.get('category', '').title() or 'your'
        answer  = f"Found {count} {cat_str} document{'s' if count != 1 else ''}"

        if filters.get('date_from') and filters.get('date_to'):
            answer += f" between {filters['date_from']} and {filters['date_to']}"
        elif filters.get('date_from'):
            answer += f" from {filters['date_from']}"
        elif filters.get('date_to'):
            answer += f" until {filters['date_to']}"

        if filters.get('vendor'):
            answer += f" from {filters['vendor']}"

        answer += '.'

        # Add total amount if available
        total = documents.aggregate(total=Sum('extracted_amount'))['total']
        if total:
            answer += f" Total amount: ₹{total:,.0f}."

        # Build sources
        sources = [
            {
                'id':       str(doc.id),
                'name':     doc.original_name,
                'category': doc.category,
            }
            for doc in documents[:5]
        ]

        return Response({
            'answer':    answer,
            'intent':    'list_documents',
            'documents': [
                {
                    'id':               str(doc.id),
                    'original_name':    doc.original_name,
                    'category':         doc.category,
                    'extracted_date':   str(doc.extracted_date) if doc.extracted_date else None,
                    'extracted_amount': float(doc.extracted_amount) if doc.extracted_amount else None,
                    'extracted_vendor': doc.extracted_vendor,
                    'summary':          doc.summary,
                    'status':           doc.status,
                }
                for doc in documents
            ],
            'sources': sources,
        }, status=status.HTTP_200_OK)
    
    def _handle_rag_query(self, request, question, history=[]):
        """Handle content questions using RAG pipeline."""
        from apps.ai_engine.embeddings import search_similar_chunks
        from apps.ai_engine.gemini import answer_query, detect_query_intent

        # Re-detect intent to get category filter for source filtering
        intent_result     = detect_query_intent(question, history)
        category_filter   = intent_result.get('filters', {}).get('category')
        date_from       = intent_result.get('filters', {}).get('date_from')
        date_to         = intent_result.get('filters', {}).get('date_to')

        # Build search query — combine last user message with context
        # so "give me more details" knows what "details" refers to
        search_query = question
        if history:
            # Find last Hita response to use as context for vague follow-ups
            last_hita = next(
                (m['content'] for m in reversed(history)
                if m['role'] == 'hita'),
                ''
            )
            # If question is vague (short, no nouns) — enrich with history
            if len(question.split()) < 5 and last_hita:
                search_query = f"{last_hita} {question}"

        relevant_chunks = search_similar_chunks(search_query, str(request.user.id))

        if not relevant_chunks:
            user_has_docs = Document.objects.filter(
                user=request.user,
                is_deleted=False
            ).exists()

            msg = ("You haven't uploaded any documents yet."
               if not user_has_docs
               else "I couldn't find relevant information for this question.")
            return Response({
                'answer': msg, 'intent': 'answer_question',
                'sources': [], 'documents': [],
            })
        
        # ── Filter chunks before passing to Gemini ──────────────────
        from datetime import date as date_type

        def chunk_matches_filters(chunk):
            try:
                doc = Document.objects.get(id=chunk['doc_id'])

                if category_filter and doc.category != category_filter:
                    return False

                if date_from and doc.extracted_date:
                    df = date_type.fromisoformat(date_from)
                    if doc.extracted_date < df:
                        return False

                if date_to and doc.extracted_date:
                    dt = date_type.fromisoformat(date_to)
                    if doc.extracted_date > dt:
                        return False
                
                # If question is about medicines/pharmacy — exclude hospitals
                medicine_keywords = ['medicine', 'medicines', 'pharmacy', 'drug', 'tablet', 'prescription']
                hospital_keywords = ['hospital', 'consultation', 'clinic', 'doctor', 'lab', 'test']

                q_lower = question.lower()
                if any(kw in q_lower for kw in medicine_keywords):
                    vendor = (doc.extracted_vendor or '').lower()
                    name   = doc.original_name.lower()
                    if any(kw in vendor or kw in name for kw in hospital_keywords):
                        return False

                return True
            except Document.DoesNotExist:
                return False
        
        # Use filtered chunks for answer — fall back to all if none match
        filtered_chunks = [c for c in relevant_chunks if chunk_matches_filters(c)]
        chunks_for_answer = filtered_chunks if filtered_chunks else relevant_chunks

        chunk_texts = [c['chunk'] for c in chunks_for_answer]
        answer      = answer_query(question, chunk_texts, history)

        # Build sources — filter by category if query is category-specific
        sources    = []
        seen_docs  = set()
        for chunk in chunks_for_answer:
            doc_id = chunk['doc_id']
            if doc_id in seen_docs:
                continue
            try:
                doc = Document.objects.get(id=doc_id)
                # Skip if category filter active and doc doesn't match
                if category_filter and doc.category != category_filter:
                    continue

                # Filter by date range if detected
                if date_from and doc.extracted_date:
                    from datetime import date
                    try:
                        df = date.fromisoformat(date_from)
                        if doc.extracted_date < df:
                            continue
                    except ValueError:
                        pass

                if date_to and doc.extracted_date:
                    from datetime import date
                    try:
                        dt = date.fromisoformat(date_to)
                        if doc.extracted_date > dt:
                            continue
                    except ValueError:
                        pass

                # Filter by vendor if detected
                vendor_filter = intent_result.get('filters', {}).get('vendor', '')
                if vendor_filter and doc.extracted_vendor:
                    if vendor_filter.lower() not in doc.extracted_vendor.lower() and \
                    doc.extracted_vendor.lower() not in vendor_filter.lower():
                        # Only skip if category filter is also active
                        if category_filter:
                            continue
                sources.append({
                    'id':       str(doc_id),
                    'name':     doc.original_name,
                    'category': doc.category,
                    
                })
                seen_docs.add(doc_id)
            except Document.DoesNotExist:
                pass

        # If category filter removed all sources — fall back to top similarity source
        if not sources and relevant_chunks:
            try:
                doc = Document.objects.get(id=relevant_chunks[0]['doc_id'])
                sources.append({
                    'id':       str(relevant_chunks[0]['doc_id']),
                    'name':     doc.original_name,
                    'category': doc.category,
                })
            except Document.DoesNotExist:
                pass

        return Response({
            'answer':    answer,
            'intent':    'answer_question',
            'sources':   sources,
            'documents': [],
        }, status=status.HTTP_200_OK)
    
    '''
    def _is_metadata_query(self, question: str) -> bool:
        """Detect if a question is asking about documents themselves, not their content."""
        metadata_keywords = [
            'what', 'which', 'how many', 'list', 'document', 'file', 'upload', 'have',
            'did i', 'do i', 'documents', 'files', 'uploaded', 'category'
        ]
        question_lower = question.lower()
        
        # Check for patterns like "what documents", "list my documents", "how many files", etc.
        for keyword in metadata_keywords:
            if keyword in question_lower:
                # Check if it's asking about documents/files
                if any(word in question_lower for word in ['document', 'file', 'upload', 'category']):
                    return True
        
        return False
    
    def _handle_metadata_query(self, request, question: str):
        """Handle metadata queries about documents."""
        user_documents = Document.objects.filter(
            user=request.user, 
            is_deleted=False,
            status__in=['processed', 'ready']  # Only include successfully processed docs
        )
        
        if not user_documents.exists():
            # Check if user has any documents at all
            all_docs = Document.objects.filter(user=request.user, is_deleted=False)
            if all_docs.exists():
                # User has docs but they're not ready
                failed_count = all_docs.filter(status='failed').count()
                processing_count = all_docs.filter(status__in=['processing', 'awaiting_ocr']).count()
                
                msg = f"You have {all_docs.count()} document(s), but they're not ready yet:\n"
                if processing_count > 0:
                    msg += f"⏳ {processing_count} currently processing\n"
                if failed_count > 0:
                    msg += f"❌ {failed_count} failed to process (check documents page for errors)"
                
                return Response({
                    'answer': msg,
                    'sources': []
                }, status=status.HTTP_200_OK)
            
            return Response({
                'answer': 'You haven\'t uploaded any documents yet. Upload your bills, medical records, receipts, or any other documents to get started!',
                'sources': []
            }, status=status.HTTP_200_OK)
        
        # Build document list response
        docs_by_category = {}
        for doc in user_documents:
            category = doc.category or 'other'
            if category not in docs_by_category:
                docs_by_category[category] = []
            docs_by_category[category].append({
                'name': doc.original_name,
                'uploaded': doc.created_at.strftime('%Y-%m-%d'),
                'status': doc.status
            })
        
        # Format answer
        answer_parts = [f"You have {user_documents.count()} document(s) ready:\n"]
        for category, docs in docs_by_category.items():
            answer_parts.append(f"\n📁 {category.capitalize()} ({len(docs)}):")
            for doc in docs:
                answer_parts.append(f"  ✅ {doc['name']} (uploaded: {doc['uploaded']})")
        
        sources = []
        for doc in user_documents[:5]:  # Include up to 5 documents as sources
            sources.append({
                'id': str(doc.id),
                'name': doc.original_name,
                'category': doc.category
            })
        
        return Response({
            'answer': '\n'.join(answer_parts),
            'sources': sources
        }, status=status.HTTP_200_OK)
    '''
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Check document processing status."""
        doc_id = request.query_params.get('document_id')
        if not doc_id:
            return Response({'error': 'document_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            document = Document.objects.get(id=doc_id, user=request.user)
            data = {
                'id': str(document.id),
                'status': document.status,
                'error_message': document.error_message
            }
            serializer = DocumentStatusSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
