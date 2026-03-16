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
