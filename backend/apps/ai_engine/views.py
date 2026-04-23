"""
Views for AI operations (RAG query interface).
"""
import logging

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
        """
        Two-stage retrieval:
        1. DB filter narrows to matching documents
        2. Embeddings rank by relevance within those docs
        3. Token budget fills context window optimally
        """
        import logging
        logger = logging.getLogger(__name__)
        from apps.ai_engine.gemini import answer_query, detect_query_intent
        from apps.ai_engine.embeddings import search_similar_chunks
        from datetime import date as date_type
        from django.db.models import Q

        intent_result   = detect_query_intent(question, history)
        category_filter = intent_result.get('filters', {}).get('category')
        date_from       = intent_result.get('filters', {}).get('date_from')
        date_to         = intent_result.get('filters', {}).get('date_to')
        vendor_filter   = intent_result.get('filters', {}).get('vendor')
        search_term     = intent_result.get('filters', {}).get('search_term')

        logger.info(f'[RAG] Question: {question}')
        logger.info(f'[RAG] Filters — cat={category_filter} '
                    f'date={date_from}~{date_to} '
                    f'vendor={vendor_filter} search={search_term}')

        search_question = question
        if history:
            last_hita = next(
                (m['content'] for m in reversed(history) if m['role'] == 'hita'), ''
            )
            if len(question.split()) < 5 and last_hita:
                search_question = f"{last_hita} {question}"

        has_filters = any([category_filter, date_from, date_to, vendor_filter])

        # ── Base queryset ────────────────────────────────────────────
        base_qs = Document.objects.filter(
            user       = request.user,
            is_deleted = False,
            status__in = ['ready', 'processed'],
        ).exclude(extracted_text__isnull=True).exclude(extracted_text='')

        # ── Set A: DB search with structured filters ─────────────────
        db_qs = base_qs

        if category_filter:
            db_qs = db_qs.filter(category=category_filter)
        if date_from:
            db_qs = db_qs.filter(
                extracted_date__gte=date_type.fromisoformat(date_from)
            )
        if date_to:
            db_qs = db_qs.filter(
                extracted_date__lte=date_type.fromisoformat(date_to)
            )
        if vendor_filter:
            db_qs = db_qs.filter(
                extracted_vendor__icontains=vendor_filter
            )
        if date_from or date_to:
            db_qs = db_qs.exclude(extracted_date__isnull=True)
        if search_term:
            db_qs = db_qs.filter(
                Q(extracted_text__icontains=search_term) |
                Q(original_name__icontains=search_term) |
                Q(summary__icontains=search_term)
            )

        db_doc_ids = set(str(i) for i in db_qs.values_list('id', flat=True))
        logger.info(f'[RAG] Set A (DB): {len(db_doc_ids)} docs')

        # ── Set B: Embeddings search ─────────────────────────────────
        similar_chunks = search_similar_chunks(
            search_question,
            str(request.user.id),
            limit=20
        )

        # Build similarity score map (best score per doc)
        embed_scores = {}
        for chunk in similar_chunks:
            doc_id = str(chunk['doc_id'])
            score  = chunk.get('similarity', 0)
            if doc_id not in embed_scores or score > embed_scores[doc_id]:
                embed_scores[doc_id] = score

        if has_filters:
            # ── Filtered mode: embeddings must respect same filters ──
            # Only keep embedding results that also pass DB filters
            # This prevents irrelevant docs polluting the context

            # Get IDs of all docs that pass the filters
            filter_passing_ids = db_doc_ids  # already computed above

            # Also include embedding docs that pass filters individually
            # (catches edge cases where extracted_text search might miss)
            embed_candidate_ids = set(embed_scores.keys())
            filtered_embed_qs   = base_qs.filter(
                id__in=embed_candidate_ids
            )

            if category_filter:
                filtered_embed_qs = filtered_embed_qs.filter(
                    category=category_filter
                )
            if date_from:
                filtered_embed_qs = filtered_embed_qs.filter(
                    extracted_date__gte=date_type.fromisoformat(date_from)
                )
            if date_to:
                filtered_embed_qs = filtered_embed_qs.filter(
                    extracted_date__lte=date_type.fromisoformat(date_to)
                )
            if date_from or date_to:
                filtered_embed_qs = filtered_embed_qs.exclude(
                    extracted_date__isnull=True
                )

            embed_doc_ids = set(
                str(i) for i in filtered_embed_qs.values_list('id', flat=True)
            )
            logger.info(f'[RAG] Set B (embeddings, filtered): {len(embed_doc_ids)} docs')

        else:
            # ── Unfiltered mode: use all embedding results ───────────
            # Apply similarity threshold to avoid very low quality matches
            SIMILARITY_THRESHOLD = 0.50
            embed_doc_ids = {
                doc_id for doc_id, score in embed_scores.items()
                if score >= SIMILARITY_THRESHOLD
            }
            logger.info(f'[RAG] Set B (embeddings, threshold={SIMILARITY_THRESHOLD}): '
                        f'{len(embed_doc_ids)} docs '
                        f'(dropped {len(embed_scores) - len(embed_doc_ids)} low score)')

        # ── Union A ∪ B ──────────────────────────────────────────────
        all_doc_ids = db_doc_ids | embed_doc_ids
        logger.info(f'[RAG] Union A∪B: {len(all_doc_ids)} docs')

        if not all_doc_ids:
            logger.info('[RAG] No docs found')
            user_has_docs = Document.objects.filter(
                user=request.user, is_deleted=False
            ).exists()
            return Response({
                'answer':    ("You haven't uploaded any documents yet."
                            if not user_has_docs
                            else "I couldn't find any matching documents for this question."),
                'intent':    'answer_question',
                'sources':   [],
                'documents': [],
            })

        # Fetch all union docs
        union_qs   = base_qs.filter(id__in=all_doc_ids)
        union_docs = {str(doc.id): doc for doc in union_qs}

        # ── Rank: DB match priority + embedding score ────────────────
        TOKEN_BUDGET   = 80000
        TOKENS_PER_DOC = 400
        MAX_DOCS       = TOKEN_BUDGET // TOKENS_PER_DOC

        def rank_score(doc_id):
            in_db    = 1.0 if doc_id in db_doc_ids else 0.0
            in_embed = embed_scores.get(doc_id, 0.0)
            return (in_db * 0.6) + (in_embed * 0.4)

        ranked_docs = sorted(
            union_docs.values(),
            key     = lambda d: rank_score(str(d.id)),
            reverse = True
        )

        if len(ranked_docs) > MAX_DOCS:
            ranked_docs = ranked_docs[:MAX_DOCS]
            logger.info(f'[RAG] Trimmed to {MAX_DOCS} docs')

        # ── Build context within token budget ────────────────────────
        context_parts = []
        sources       = []
        token_count   = 0

        for doc in ranked_docs:
            doc_text = (
                f"Document: {doc.original_name}\n"
                f"Date: {doc.extracted_date}\n"
                f"Category: {doc.category}\n"
                f"Vendor: {doc.extracted_vendor or 'Unknown'}\n"
                f"Amount: ₹{doc.extracted_amount or 'Unknown'}\n"
                f"Content: {doc.extracted_text[:800]}"
            )
            doc_tokens = len(doc_text) // 4

            if token_count + doc_tokens > TOKEN_BUDGET:
                logger.info(f'[RAG] Token budget reached at {len(context_parts)} docs')
                break

            context_parts.append(doc_text)
            sources.append({
                'id':       str(doc.id),
                'name':     doc.original_name,
                'category': doc.category,
            })
            token_count += doc_tokens
            logger.info(
                f'[RAG]   + {doc.original_name} '
                f'(db={str(doc.id) in db_doc_ids} '
                f'embed={embed_scores.get(str(doc.id), 0):.2f} '
                f'rank={rank_score(str(doc.id)):.2f})'
            )

        logger.info(f'[RAG] Sending {len(context_parts)} docs '
                    f'(~{token_count} tokens) to Gemini')

        # Medicine query — filter hospital sources from display
        q_lower = question.lower()
        if any(kw in q_lower for kw in
            ['medicine', 'medicines', 'taking', 'prescription']):
            sources = [
                s for s in sources
                if not any(kw in s['name'].lower()
                        for kw in ['hospital', 'miot', 'heart', 'clinic'])
            ]

        context = '\n\n---\n\n'.join(context_parts)
        answer  = answer_query(search_question, [context], history)

        logger.info(f'[RAG] Answer: {answer[:150]}')

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
