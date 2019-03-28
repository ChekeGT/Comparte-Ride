"""Users app urls configuration."""

# Django
from django.urls import path, include

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import UserManagementViewSet

router = DefaultRouter()
router.register(r'', UserManagementViewSet, base_name='users')

app_name = 'Users'

urlpatterns = [
    path('', include(router.urls))
]
