"""Circles app urls configuration and mapping"""

# Django
from django.urls import path

# Views
from .views import list_circles, create_circle



app_name = 'Circles'

urlpatterns = [
    path('list/', list_circles, name='list'),
    path('create/', create_circle, name='create')
]
