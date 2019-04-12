"""Ride Model Related views."""

# Django REST Framework

# Mixins
from rest_framework.mixins import (
    CreateModelMixin
)
from cride.utils.mixins import AddCircleMixin

# Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions import IsCircleActiveMember

# Serializers
from cride.rides.serializers import CreateRideSerializer


class RideViewSet(
    AddCircleMixin,
    CreateModelMixin,
):
    """Pending docs."""

    serializer_class = CreateRideSerializer

    permission_classes = [
        IsAuthenticated,
        IsCircleActiveMember,
    ]

    def get_serializer_context(self):
        """Modifies the serializer context adding the current circle to the context."""
        
        context = super(RideViewSet, self).get_serializer_context()

        context['circle'] = self.circle

        return context
    
