"""Users app urls configuration."""

# Django
from django.urls import path

# Views
from .views import UserLoginAPIView, UserSignupAPIView, UserVerifyAPIView


app_name = 'Users'

urlpatterns = [
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('signup/', UserSignupAPIView.as_view(), name='signup'),
    path('verify/', UserVerifyAPIView.as_view(), name='verify'),
]
