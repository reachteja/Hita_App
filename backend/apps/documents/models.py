"""
Document models for Hita.
Handles document metadata, storage, and processing status.
"""
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

DOCUMENT_CATEGORIES = [
    ('grocery', 'Grocery'),
    ('medical', 'Medical'),
    ('maintenance', 'Maintenance'),
    ('personal', 'Personal'),
    ('events', 'Events'),
    ('finance', 'Finance'),
    ('other', 'Other'),
]

DOCUMENT_STATUS = [
    ('uploaded', 'Uploaded'),
    ('processing', 'Processing'),
    ('ready', 'Ready'),
    ('failed', 'Failed'),
]


class Document(models.Model):
    """Document model - stores metadata about uploaded documents."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    
    # File information
    original_name = models.CharField(max_length=500)
    file_path = models.CharField(max_length=1000)
    file_type = models.CharField(max_length=100)  # MIME type
    file_size = models.BigIntegerField()  # bytes
    
    # AI extracted information
    category = models.CharField(max_length=50, choices=DOCUMENT_CATEGORIES, default='other')
    extracted_text = models.TextField(blank=True, null=True)  # First 5000 chars
    extracted_date = models.DateField(blank=True, null=True)
    extracted_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    extracted_vendor = models.CharField(max_length=500, blank=True)
    summary = models.TextField(blank=True)
    
    # Processing status
    status = models.CharField(max_length=20, choices=DOCUMENT_STATUS, default='uploaded')
    celery_task_id = models.CharField(max_length=255, blank=True)
    error_message = models.TextField(blank=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'documents_document'
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.original_name
