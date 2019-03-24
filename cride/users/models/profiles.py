"""Profile model and related models declaration."""

# Django

from django.db import models

# Models
from cride.utils.models import CRideModel
from cride.users.models import User


class Profile(CRideModel):
    """Profile Model Declaration

    It's a proxy model to the user but its difference
    is that this one is for public data, so you could
    find in the Profile things like bio, picture...
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    picture = models.ImageField(
        upload_to='users/pictures/',
        blank=True,
        null=True
    )

    biography = models.TextField(
        max_length=500,
        blank=True
    )

    # Statistics

    rides_taken = models.PositiveIntegerField(default=0)
    rides_offered = models.PositiveIntegerField(default=0)

    reputation = models.FloatField(
        default=5.0,
        help_text="User reputation based on the rides that he has taken or offered."
    )

    def __str__(self):
        """Returns user's str representation"""
        return str(self.user)
