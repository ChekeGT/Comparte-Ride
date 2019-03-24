"""Users app models module."""

# Django
from django.db import models
from django.contrib.auth.models import AbstractUser

# Utilities

from cride.utils.models import CRideModel


class User(CRideModel, AbstractUser):
    """ User model.

       Extend from Django's Abstract User, change the username field
       to email and add some extra fields.
    """
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': 'A user with this email already exists.'
        }
    )

    USERNAME_FIELD =  'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    phone_number = models.CharField(
        blank=True,
        max_length=17
    )

    is_client = models.BooleanField(
        default=True,
        help_text=(
            'Help easily distinguish users and perform queries.'
            'Clients are the main type of user.'
        )
    )

    is_verified = models.BooleanField(
        default=True,
        help_text='Set to true when the user have verified its email address.'
    )
