"""
Django admin configuration for users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import HitaUser


@admin.register(HitaUser)
class HitaUserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'is_active', 'consent_given', 'created_at']
    list_filter = ['is_active', 'consent_given', 'created_at']
    search_fields = ['email', 'full_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'id')}),
        ('Compliance', {'fields': ('consent_given', 'consent_given_at')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'consent_given'),
        }),
    )
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_login']
