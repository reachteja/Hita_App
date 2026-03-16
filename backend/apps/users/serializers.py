"""
Serializers for user authentication and registration.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile display."""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True)
    consent_given = serializers.BooleanField(required=True)
    
    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'confirm_password', 'consent_given']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        
        if attrs.get('consent_given') is not True:
            raise serializers.ValidationError({'consent_given': 'You must accept the terms and conditions'})
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            consent_given=validated_data.get('consent_given', False)
        )
        # consent_given_at will be set automatically in the model's save() method
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        from django.contrib.auth import authenticate
        
        email = attrs.get('email')
        password = attrs.get('password')
        
        # Use email field specifically for custom user model authentication
        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            raise serializers.ValidationError('Invalid email or password')
        
        if not user.is_active:
            raise serializers.ValidationError('User account is inactive')
        
        attrs['user'] = user
        return attrs


class TokenSerializer(serializers.Serializer):
    """Serializer for JWT tokens."""
    
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
