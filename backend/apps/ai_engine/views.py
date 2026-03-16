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
        """Ask a question about user's documents (RAG)."""
        serializer = QuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        question = serializer.validated_data['question']
        
        try:
            # Check if this is a metadata query (asking about documents themselves)
            if self._is_metadata_query(question):
                return self._handle_metadata_query(request, question)
            
            # Otherwise, do semantic search on document content
            from apps.ai_engine.embeddings import search_similar_chunks
            from apps.ai_engine.gemini import answer_query
            
            # Search for relevant chunks
            relevant_chunks = search_similar_chunks(question, str(request.user.id))
            
            if not relevant_chunks:
                # Check if user has any documents at all
                user_has_docs = Document.objects.filter(user=request.user, is_deleted=False).exists()
                if not user_has_docs:
                    return Response({
                        'answer': 'You haven\'t uploaded any documents yet. Upload documents like bills, medical records, or receipts to get started!',
                        'sources': []
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'answer': 'I did not find information in your documents that matches this question. Try asking about specific details from your uploaded documents.',
                        'sources': []
                    }, status=status.HTTP_200_OK)
            
            # Extract chunk texts
            chunk_texts = [c['chunk'] for c in relevant_chunks]
            
            # Generate answer
            answer = answer_query(question, chunk_texts)
            
            # Build sources list
            sources = []
            seen_docs = set()
            for chunk in relevant_chunks:
                doc_id = chunk['doc_id']
                if doc_id not in seen_docs:
                    doc = Document.objects.get(id=doc_id)
                    sources.append({
                        'id': str(doc_id),
                        'name': doc.original_name,
                        'category': doc.category
                    })
                    seen_docs.add(doc_id)
            
            response_data = {
                'answer': answer,
                'sources': sources
            }
            
            serializer = QueryResponseSerializer(response_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'Query failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
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
