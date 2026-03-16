"""
URL routes for user authentication.
"""
from django.urls import path
from .views import AuthViewSet

auth_register = AuthViewSet.as_view({'post': 'register'})
auth_login = AuthViewSet.as_view({'post': 'login'})
auth_logout = AuthViewSet.as_view({'post': 'logout'})
auth_profile = AuthViewSet.as_view({'get': 'profile'})
auth_profile_update = AuthViewSet.as_view({'patch': 'profile_update'})

urlpatterns = [
    path('register/', auth_register, name='register'),
    path('login/', auth_login, name='login'),
    path('logout/', auth_logout, name='logout'),
    path('profile/', auth_profile, name='profile'),
    path('profile/', auth_profile_update, name='profile_update'),
]
