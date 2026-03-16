"""
URL routes for documents.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet

router = DefaultRouter()
router.register(r'', DocumentViewSet, basename='document')

urlpatterns = router.urls

# Add custom upload endpoint
urlpatterns += [
    path('upload/', DocumentViewSet.as_view({'post': 'upload'}), name='document-upload'),
]
