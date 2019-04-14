"""Circles app configuration of the admin of it's models."""


# Django
from django.contrib import admin

# Models
from .models import Circle


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    """Model admin configuration of circle model."""

    list_display = [
        'slug_name',
        'name',
        'is_public',
        'is_verified',
        'is_limited',
        'members_limit'
    ]

    search_fields = [
        'slug_name',
        'name'
    ]

    list_filter = [
        'is_public',
        'is_verified',
        'is_limited'
    ]
