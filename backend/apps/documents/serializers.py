"""
Serializers for document upload and management.
"""
from rest_framework import serializers
from .models import Document, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Tag
        fields = ['id', 'name']

class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for document display and management."""
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'original_name', 'file_type', 'file_size',
            'category', 'summary', 'extracted_date', 'extracted_amount',
            'extracted_vendor', 'status', 'error_message', 'created_at','tags',
        ]
        read_only_fields = [
            'id', 'file_path', 'file_type', 'file_size',
            'extracted_text', 'extracted_date', 'extracted_amount',
            'extracted_vendor', 'summary', 'status', 'error_message',
            'celery_task_id', 'created_at','tags',
        ]


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for document upload."""
    
    file = serializers.FileField(write_only=True)
    
    class Meta:
        model = Document
        fields = ['file']
    
    def create(self, validated_data):
        file = validated_data.pop('file')
        document = Document(
            original_name=file.name,
            file_type=file.content_type,
            file_size=file.size
        )
        # File path will be set in views
        return document


class DocumentCategoryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating document category."""
    
    class Meta:
        model = Document
        fields = ['category']
