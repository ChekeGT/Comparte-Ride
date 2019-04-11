"""Rides app configuration."""

# Django
from django.apps import AppConfig


class RidesConfig(AppConfig):
    """RidesConfig class that inherits from AppConfig.

    Provides the necessary data for this app to be considered as one.
    """
    name = 'cride.rides'
    verbose_name = 'Rides'
