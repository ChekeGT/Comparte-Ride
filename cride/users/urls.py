"""Users app urls configuration."""

# Django
from django.urls import path

# Views
from .views import UserLoginAPIView


app_name = 'Users'

urlpatterns = [
    path('login/', UserLoginAPIView.as_view(), name='login')
]
