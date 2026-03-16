"""
URL routes for AI operations.
"""
from django.urls import path
from .views import AIViewSet

ai_query = AIViewSet.as_view({'post': 'query'})
ai_status = AIViewSet.as_view({'get': 'status'})

urlpatterns = [
    path('query/', ai_query, name='ai-query'),
    path('status/', ai_status, name='ai-status'),
]
