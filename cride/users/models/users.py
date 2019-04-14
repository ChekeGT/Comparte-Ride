"""User Model Declaration."""

# Django
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    PHONE_REGEX_VALIDATOR = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message='Phone number must be entered in the format: +999999999. Up to 15 digits allowed.'
    )
    phone_number = models.CharField(
        blank=True,
        max_length=17,
        validators=[PHONE_REGEX_VALIDATOR]
    )

    is_client = models.BooleanField(
        default=True,
        help_text=(
            'Help easily distinguish users and perform queries.'
            'Clients are the main type of user.'
        )
    )

    is_verified = models.BooleanField(
        default=False,
        help_text='Set to true when the user have verified its email address.'
    )

    def __str__(self):
        """Returns the username to be used as the name of this model."""
        return self.get_short_name()

    def get_short_name(self):
        """Returns the username."""
        return self.username
