"""Users app configuration."""

# Django
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """UserConfig class that inherits from AppConfig.

    Provides the necessary data for this app to be considered as one.
    """
    name = 'cride.users'
    verbose_name = 'Users'
