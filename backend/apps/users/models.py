"""
User models for Hita authentication.
Custom HitaUser model with email-based auth and DPDP compliance.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid

class HitaUserManager(BaseUserManager):
    """Custom user manager for HitaUser."""
    
    def create_user(self, email, password=None, full_name='', **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, full_name='', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, full_name, **extra_fields)


class HitaUser(AbstractBaseUser, PermissionsMixin):
    """Custom Hita user model with email-based authentication."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=254)
    full_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # DPDP Act 2023 compliance
    consent_given = models.BooleanField(default=False, help_text='User consent to terms and conditions')
    consent_given_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = HitaUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    class Meta:
        db_table = 'auth_hitauser'
        verbose_name = 'Hita User'
        verbose_name_plural = 'Hita Users'
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        # Record consent timestamp if consent just given
        if self.consent_given and not self.consent_given_at:
            self.consent_given_at = timezone.now()
        super().save(*args, **kwargs)
