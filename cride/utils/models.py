"""Utils app models module."""

# Django
from django.db import models


class CRideModel(models.Model):
    """Comparte Ride Base Model.

    CRideModel acts as an abstract base class from which every
    other model in the project will inherit. This class provides
    tables with the following attributes:
        + created = DateTimeField --> Store the datetime the object was created.
        + modified = DateTimeField --> Store the last datetime the object was modified.
    """

    created = models.DateTimeField(
        auto_now_add=True,
        help_text='Date Time on which the object was created.'
    )
    modified = models.DateTimeField(
        auto_now=True,
        help_text='Date Time on which the object was last modified.'
    )

    class Meta:
        """Meta attributes."""

        abstract = True
        ordering = ['-created', '-modified']

