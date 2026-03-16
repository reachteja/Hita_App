"""
Serializers for AI operations.
"""
from rest_framework import serializers


class QuerySerializer(serializers.Serializer):
    """Serializer for document query."""
    
    question = serializers.CharField(max_length=1000)


class QueryResponseSerializer(serializers.Serializer):
    """Serializer for query response."""
    
    answer = serializers.CharField()
    sources = serializers.ListField(child=serializers.DictField())


class DocumentStatusSerializer(serializers.Serializer):
    """Serializer for document processing status."""
    
    id = serializers.CharField()
    status = serializers.CharField()
    error_message = serializers.CharField(required=False)
