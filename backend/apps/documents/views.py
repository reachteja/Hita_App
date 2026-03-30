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
from rest_framework.views import APIView

from .models import Document, Tag
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
        queryset = self.get_queryset().prefetch_related('tags')
        
        # Filter by category if provided
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Filter by tags (multiple tags = AND filter)
        tag_names = request.query_params.getlist('tag')
        if tag_names:
            for tag_name in tag_names:
                queryset = queryset.filter(tags__name=tag_name)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        """Hard delete document — removes file, embeddings, tags, and DB record."""
        document = self.get_object()

        # Delete physical file
        if os.path.exists(document.file_path):
            os.remove(document.file_path)

        # Delete embeddings from pgvector
        try:
            from apps.ai_engine.embeddings import delete_document_embeddings
            delete_document_embeddings(str(document.id))
        except Exception:
            pass

        # Hard delete document record
        document.delete()

        # Clean up orphaned tags — tags with no remaining documents
        Tag.objects.filter(
            user=request.user,
            documents__isnull=True
        ).delete()

        return Response(
            {'message': 'Document permanently deleted'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], url_path='retry')
    def retry(self, request, pk=None):
        """Retry processing a failed document."""
        document = self.get_object()

        if document.status not in ['failed', 'processing']:
            return Response(
                {'error': 'Only failed documents can be retried'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Reset status
        document.status        = 'processing'
        document.error_message = ''
        document.save(update_fields=['status', 'error_message'])

        # Re-queue Celery task
        try:
            from apps.ai_engine.tasks import process_document
            task = process_document.delay(str(document.id))
            document.celery_task_id = task.id
            document.save(update_fields=['celery_task_id'])
        except Exception as e:
            document.status        = 'failed'
            document.error_message = f'Retry failed: {str(e)}'
            document.save(update_fields=['status', 'error_message'])
            return Response(
                {'error': 'Could not queue retry. Is Celery running?'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = self.get_serializer(document)
        return Response({
            'message':  'Document queued for reprocessing',
            'document': serializer.data,
        })
    
    @action(detail=False, methods=['get', 'post'], url_path='tags')
    def list_tags(self, request):
        """GET all user tags / POST create new tag."""
        if request.method == 'GET':
            tags = Tag.objects.filter(
                    user=request.user,
                    documents__is_deleted=False,        # tag has at least one non-deleted doc
                    ).distinct().order_by('name')
            return Response({
                'tags': [{'id': str(t.id), 'name': t.name} for t in tags]
            })

        # POST — create tag
        name = request.data.get('name', '').strip().lower()
        if not name:
            return Response({'error': 'Tag name required'}, status=400)
        if len(name) > 50:
            return Response({'error': 'Tag name too long — max 50 characters'}, status=400)

        tag, created = Tag.objects.get_or_create(user=request.user, name=name)
        return Response({
            'id':      str(tag.id),
            'name':    tag.name,
            'created': created,
        }, status=201 if created else 200)


    @action(detail=False, methods=['delete'], url_path='tags/(?P<tag_id>[^/.]+)')
    def delete_tag(self, request, tag_id=None):
        """Delete a tag — removes from all documents too."""
        try:
            tag = Tag.objects.get(id=tag_id, user=request.user)
            tag.delete()
            return Response({'message': 'Tag deleted'})
        except Tag.DoesNotExist:
            return Response({'error': 'Tag not found'}, status=404)


    @action(detail=True, methods=['post', 'delete'], url_path='tags')
    def document_tags(self, request, pk=None):
        """POST add tag to document / DELETE remove tag from document."""
        document = self.get_object()

        if request.method == 'POST':
            name = request.data.get('name', '').strip().lower()
            if not name:
                return Response({'error': 'Tag name required'}, status=400)

            tag, _ = Tag.objects.get_or_create(user=request.user, name=name)
            document.tags.add(tag)

        elif request.method == 'DELETE':
            tag_id = request.data.get('tag_id')
            if not tag_id:
                return Response({'error': 'tag_id required'}, status=400)
            try:
                tag = Tag.objects.get(id=tag_id, user=request.user)
                document.tags.remove(tag)
            except Tag.DoesNotExist:
                pass

        all_tags = [{'id': str(t.id), 'name': t.name} for t in document.tags.all()]
        return Response({'tags': all_tags})
    
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
