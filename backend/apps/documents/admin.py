"""
Django admin configuration for documents app.
"""
from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['original_name', 'user', 'category', 'status', 'file_size', 'created_at']
    list_filter = ['category', 'status', 'created_at', 'is_deleted']
    search_fields = ['original_name', 'user__email', 'extracted_vendor']
    ordering = ['-created_at']
    readonly_fields = ['id', 'file_path', 'celery_task_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('File Info', {
            'fields': ('id', 'user', 'original_name', 'file_path', 'file_type', 'file_size')
        }),
        ('Processing', {
            'fields': ('status', 'celery_task_id', 'error_message')
        }),
        ('AI Extracted', {
            'fields': ('category', 'extracted_text', 'extracted_date', 'extracted_amount', 'extracted_vendor', 'summary')
        }),
        ('Status', {
            'fields': ('is_deleted', 'created_at', 'updated_at')
        }),
    )
