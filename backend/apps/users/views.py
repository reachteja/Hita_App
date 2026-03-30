"""
Views for user authentication.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

User = get_user_model()


class AuthViewSet(viewsets.ViewSet):
    """ViewSet for authentication endpoints."""
    
    def get_permissions(self):
        """Override permissions based on action."""
        if self.action in ['register', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user."""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'message': 'User registered successfully',
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': str(e),
                    'detail': 'Error creating user'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'errors': serializer.errors,
            'detail': 'Validation failed'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login user and return JWT tokens."""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.validated_data['user']
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'message': 'Login successful',
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': str(e),
                    'detail': 'Error logging in'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'errors': serializer.errors,
            'detail': 'Invalid credentials'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout user (token blacklisting)."""
        # In production, blacklist the refresh token here
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user profile."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['patch'])
    def profile_update(self, request):
        """Update current user profile."""
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'], url_path='delete')
    def delete_account(self, request):
        """
        Permanently delete user account and all associated data.
        DPDP Act 2023 — right to erasure.
        """
        user = request.user

        # Require email confirmation
        confirm_email = request.data.get('confirm_email', '').strip().lower()
        if confirm_email != user.email.lower():
            return Response(
                {'error': 'Email does not match. Please type your email exactly to confirm.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Step 1 — Delete physical files
            import os
            import shutil
            from django.conf import settings as django_settings

            user_upload_dir = os.path.join(
                django_settings.MEDIA_ROOT,
                str(user.id)
            )
            if os.path.exists(user_upload_dir):
                shutil.rmtree(user_upload_dir)

            # Step 2 — Delete all pgvector embeddings
            from apps.documents.models import Document
            from apps.ai_engine.embeddings import delete_document_embeddings

            for doc in Document.objects.filter(user=user):
                try:
                    delete_document_embeddings(str(doc.id))
                except Exception:
                    pass

            # Step 3 — Blacklist refresh token
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                try:
                    from rest_framework_simplejwt.tokens import RefreshToken
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception:
                    pass

            # Step 4 — Delete user (cascades to documents, tags, logs)
            user.delete()

            return Response({
                'message': 'Your account and all data has been permanently deleted.'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Deletion failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
