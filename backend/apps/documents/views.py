"""
Views for document management.
"""
import os
import uuid
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer, DocumentCategoryUpdateSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for document management."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentSerializer
    
    def get_queryset(self):
        """Return documents for current user only."""
        return Document.objects.filter(user=self.request.user, is_deleted=False)
    
    def list(self, request, *args, **kwargs):
        """List user's documents with optional category filter."""
        queryset = self.get_queryset()
        
        # Filter by category if provided
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload a new document."""
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check file size
        max_size = settings.MAX_UPLOAD_SIZE
        if file.size > max_size:
            return Response(
                {'error': f'File size exceeds limit: {settings.MAX_UPLOAD_SIZE_MB}MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check file type
        if file.content_type not in settings.ALLOWED_FILE_TYPES:
            return Response(
                {'error': f'File type not allowed: {file.content_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create document record and process
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Generate unique filename
            ext = os.path.splitext(file.name)[1]
            unique_filename = f"{uuid.uuid4()}{ext}"
            
            # Create user upload directory
            user_upload_dir = os.path.join(settings.MEDIA_ROOT, str(request.user.id))
            os.makedirs(user_upload_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(user_upload_dir, unique_filename)
            with open(file_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            
            # Create document record
            document = Document.objects.create(
                user=request.user,
                original_name=file.name,
                file_path=file_path,
                file_type=file.content_type,
                file_size=file.size,
                status='processing'
            )
            
            # Try async processing first, fallback to sync
            try:
                from apps.ai_engine.tasks import process_document
                task = process_document.delay(str(document.id))
                document.celery_task_id = task.id
                document.save(update_fields=['celery_task_id'])
            except Exception as celery_err:
                logger.warning(f"Celery failed for {document.id}: {str(celery_err)}. Using sync processing.")
                
                # Synchronous fallback
                try:
                    from apps.documents.utils import extract_text, scrub_pii, chunk_text
                    from apps.ai_engine.gemini import categorise_document
                    from apps.ai_engine.embeddings import store_embeddings
                    
                    raw_text = extract_text(document.file_path)
                    if not raw_text or not raw_text.strip():
                        document.status = 'failed'
                        document.error_message = 'No text could be extracted from document'
                        document.save()
                    else:
                        clean_text = scrub_pii(raw_text)
                        chunks = chunk_text(clean_text)
                        
                        if chunks:
                            store_embeddings(str(document.id), chunks)
                        
                        # Try to categorize with Gemini
                        try:
                            ai_result = categorise_document(clean_text)
                            document.category = ai_result.get('category', 'other')
                            document.summary = ai_result.get('summary', '')
                        except Exception as ai_err:
                            logger.warning(f"Gemini failed: {str(ai_err)}")
                            document.category = 'other'
                            document.summary = 'Processing complete (Gemini unavailable)'
                        
                        document.extracted_text = raw_text[:5000]
                        document.status = 'processed'
                        document.error_message = ''
                        document.save()
                        
                except Exception as sync_err:
                    document.status = 'failed'
                    document.error_message = str(sync_err)[:500]
                    document.save()
                    logger.error(f"Sync failed: {str(sync_err)}")
            
            # Return the processed document
            serializer = DocumentSerializer(document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Upload failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
