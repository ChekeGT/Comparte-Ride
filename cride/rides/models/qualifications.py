"""Qualification model."""

# Django
from django.db import models

# Models
from cride.utils.models import CRideModel


class Qualification(CRideModel):
    """Qualification model."""

    user = models.ForeignKey('users.User', on_delete=models.SET_DEFAULT, default=0)
    score = models.FloatField(default=0)

    def __str__(self):
        """Returns object string representation."""

        return f'{self.user} rated {self.score}'
