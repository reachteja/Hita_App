"""
Views for AI operations (RAG query interface).
"""
import logging, traceback

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.documents.models import Document
from .serializers import QuerySerializer, QueryResponseSerializer, DocumentStatusSerializer

from django.db.models import Q, Sum
from apps.ai_engine.gemini import answer_query, detect_query_intent
from apps.ai_engine.embeddings import search_similar_chunks
from datetime import date as date_type

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
            
            logger = logging.getLogger(__name__)
            logger.error(f'Query failed: {str(e)}')
            logger.error(traceback.format_exc())
            return Response(
                {'error': f'Query failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @staticmethod
    def _apply_filters(queryset, filters: dict):
        from datetime import date as date_type
        if filters.get('category'):
            queryset = queryset.filter(category=filters['category'])
        if filters.get('date_from'):
            queryset = queryset.filter(extracted_date__gte=date_type.fromisoformat(filters['date_from']))
        if filters.get('date_to'):
            queryset = queryset.filter(extracted_date__lte=date_type.fromisoformat(filters['date_to']))
        if filters.get('vendor'):
            queryset = queryset.filter(extracted_vendor__icontains=filters['vendor'])
        if filters.get('date_from') or filters.get('date_to'):
            queryset = queryset.exclude(extracted_date__isnull=True)
        return queryset

    def _handle_list_documents(self, request, question, filters):
        """Handle document search/list queries with Gemini-extracted filters."""
        
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
    
    def _get_relevant_text(self, doc, search_term: str, max_chars: int = 1500) -> str:
        """Return most relevant section of document text based on search term."""
        text = doc.extracted_text or ''
        if not text:
            return ''
        if not search_term:
            return text[:max_chars]

        pos = text.lower().find(search_term.lower())
        if pos == -1:
            return text[:max_chars]

        # Start from sheet header before the term
        # Find the nearest 'Sheet:' marker before pos
        sheet_marker = text.rfind('Sheet:', 0, pos)
        start  = sheet_marker if sheet_marker != -1 else max(0, pos - 200)
        end    = min(len(text), start + max_chars)
        prefix = '...\n' if start > 0 else ''
        return prefix + text[start:end]


    def _handle_rag_query(self, request, question, history: list = None):
        
        logger = logging.getLogger(__name__)
        if history is None:
            history = []
        try:
        
            intent_result   = detect_query_intent(question, history)
            category_filter = intent_result.get('filters', {}).get('category')
            date_from       = intent_result.get('filters', {}).get('date_from')
            date_to         = intent_result.get('filters', {}).get('date_to')
            vendor_filter   = intent_result.get('filters', {}).get('vendor')

            # Ignore 'other' — means unclassified
            if category_filter == 'other':
                category_filter = None

            logger.info(f'[RAG] Question: {question}')
            logger.info(f'[RAG] Filters — cat={category_filter} '
                        f'date={date_from}~{date_to} vendor={vendor_filter}')

            # Enrich vague follow-ups
            search_question = question
            if history:
                last_hita = next(
                    (m['content'] for m in reversed(history)
                    if m['role'] == 'hita'), ''
                )
                if len(question.split()) < 5 and last_hita:
                    search_question = f"{last_hita} {question}"

            has_structured_filters = any([
                category_filter, date_from, date_to, vendor_filter
            ])

            # ── Base queryset ─────────────────────────────────────────
            base_qs = Document.objects.filter(
                user       = request.user,
                is_deleted = False,
                status__in = ['ready', 'processed'],
            ).exclude(extracted_text__isnull=True).exclude(extracted_text='')

            # ── Embeddings search — always run first ──────────────────
            similar_chunks = search_similar_chunks(
                search_question,
                str(request.user.id),
                limit=20
            )

            # Best similarity score per doc
            embed_scores = {}
            for chunk in similar_chunks:
                doc_id = str(chunk['doc_id'])
                score  = chunk.get('similarity', 0)
                if doc_id not in embed_scores or score > embed_scores[doc_id]:
                    embed_scores[doc_id] = score

            # Adaptive threshold — only keep docs close to top score
            if embed_scores:
                top_score = max(embed_scores.values())
                threshold = max(0.60, top_score - 0.10)
            else:
                threshold = 0.60

            embed_doc_ids = {
                doc_id for doc_id, score in embed_scores.items()
                if score >= threshold
            }
            logger.info(
                f'[RAG] Embeddings: top={top_score:.2f} '
                f'threshold={threshold:.2f} '
                f'kept={len(embed_doc_ids)} '
                f'dropped={len(embed_scores)-len(embed_doc_ids)}'
            )

            # ── Set A: DB structured filters (if any) ────────────────
            # Only apply when user explicitly mentions category/date/vendor
            if has_structured_filters:
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

                db_doc_ids = set(
                    str(i) for i in db_qs.values_list('id', flat=True)
                )

                # Union: DB results + embedding results filtered to same criteria
                # Embedding results must also pass structured filters
                filtered_embed_ids = set(
                    str(i) for i in base_qs.filter(
                        id__in=embed_doc_ids
                    ).filter(
                        category=category_filter
                        if category_filter else Q()
                    ).values_list('id', flat=True)
                ) if category_filter else embed_doc_ids

                all_doc_ids = db_doc_ids | (filtered_embed_ids & embed_doc_ids)
                logger.info(
                    f'[RAG] Set A (DB structured): {len(db_doc_ids)} docs'
                )

            else:
                # No structured filters — pure embeddings result
                db_doc_ids  = set()
                all_doc_ids = embed_doc_ids
                logger.info('[RAG] No structured filters — pure embeddings')

            logger.info(f'[RAG] Final candidate pool: {len(all_doc_ids)} docs')

            if not all_doc_ids:
                user_has_docs = Document.objects.filter(
                    user=request.user, is_deleted=False
                ).exists()
                return Response({
                    'answer':    ("You haven't uploaded any documents yet."
                                if not user_has_docs
                                else "I couldn't find any matching documents."),
                    'intent':    'answer_question',
                    'sources':   [],
                    'documents': [],
                })

            # ── Fetch and rank ────────────────────────────────────────
            union_qs   = base_qs.filter(id__in=all_doc_ids)
            union_docs = {str(doc.id): doc for doc in union_qs}

            def rank_score(doc_id):
                in_db    = 1.0 if doc_id in db_doc_ids else 0.0
                in_embed = embed_scores.get(doc_id, 0.0)
                return (in_db * 0.6) + (in_embed * 0.4)

            TOKEN_BUDGET = 80000
            MAX_DOCS     = TOKEN_BUDGET // 400

            ranked_docs = sorted(
                union_docs.values(),
                key     = lambda d: rank_score(str(d.id)),
                reverse = True
            )[:MAX_DOCS]

            # ── Build context ─────────────────────────────────────────
            context_parts = []
            sources       = []
            token_count   = 0

            for doc in ranked_docs:
                try:
                    relevant_text = self._get_relevant_text(doc, None)
                except Exception:
                    relevant_text = (doc.extracted_text or '')[:800]

                doc_text = (
                    f"=== Document: {doc.original_name} ===\n"
                    f"Date: {doc.extracted_date}\n"
                    f"Category: {doc.category}\n"
                    f"Vendor: {doc.extracted_vendor or 'Unknown'}\n"
                    f"Amount: ₹{doc.extracted_amount or 'Unknown'}\n"
                    f"Content:\n{relevant_text}"
                )
                doc_tokens = len(doc_text) // 4

                if token_count + doc_tokens > TOKEN_BUDGET:
                    logger.info(f'[RAG] Token budget at {len(context_parts)} docs')
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
                    f'(embed={embed_scores.get(str(doc.id),0):.2f} '
                    f'rank={rank_score(str(doc.id)):.2f})'
                )

            logger.info(
                f'[RAG] Sending {len(context_parts)} docs '
                f'(~{token_count} tokens) to Gemini'
            )

            context = '\n\n---\n\n'.join(context_parts)
            result  = answer_query(search_question, [context], history)
            
            # Handle both old string return and new dict return
            if isinstance(result, dict):
                answer      = result.get('answer', '')
                used_sources = result.get('used_sources', [])
                used_sections = result.get('used_sections', [])
            else:
                answer       = result
                used_sources = []
                used_sections = []

            logger.info(f'[RAG] Answer: {answer[:150]}')
            logger.info(f'[RAG] Used sources: {used_sources}')
            logger.info(f'[RAG] Used sections: {used_sections}')

            # Filter sources to only ones Gemini actually used
            if used_sources:
                # Match by filename — case insensitive partial match
                filtered_sources = []
                for s in sources:
                    doc_name = s['name']
                    # Check if this doc appears in used_sources
                    # Handle both "IN_OUT_CASH.xlsx > OUT" and "IN_OUT_CASH.xlsx"
                    for used in used_sources:
                        used_doc = used.split('>')[0].strip()  # get doc name part
                        if (used_doc.lower() in doc_name.lower() or
                            doc_name.lower() in used_doc.lower()):

                            # Add sheet info to source if available
                            if '>' in used:
                                sheet = used.split('>', 1)[1].strip()
                                s = {**s, 'sheet': sheet}

                            filtered_sources.append(s)
                            break

                # Fallback: if nothing matched, keep all sources
                sources = filtered_sources if filtered_sources else sources

            return Response({
                'answer':    answer,
                'intent':    'answer_question',
                'sources':   sources,
                'documents': [],
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'[RAG] Error: {str(e)}')
            logger.error(traceback.format_exc())
            return Response(
                {'error': f'Query failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    
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
