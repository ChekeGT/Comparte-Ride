"""Ride Model Related views."""

# Django REST Framework

# Mixins
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
)
from cride.utils.mixins import AddCircleMixin

# Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions import IsCircleActiveMember

# Serializers
from cride.rides.serializers import (
    CreateRideSerializer,
    RideModelSerializer
)

# Utilities
from django.utils import timezone
from datetime import timedelta

# Filters
from rest_framework.filters import SearchFilter, OrderingFilter


class RideViewSet(
    AddCircleMixin,
    ListModelMixin,
    CreateModelMixin,
):
    """Pending docs."""

    permission_classes = [
        IsAuthenticated,
        IsCircleActiveMember,
    ]

    filter_backends = (SearchFilter, OrderingFilter)

    search_fields = ('departure_location', 'arrival_location')

    ordering_fields = ('departure_date', 'arrival_date', 'available_seats')

    ordering = ('departure_date', 'arrival_date', 'available_seats')

    def get_serializer_context(self):
        """Modifies the serializer context adding the current circle to the context."""
        
        context = super(RideViewSet, self).get_serializer_context()

        context['circle'] = self.circle

        return context

    def get_serializer_class(self):
        """Returns serializer class based on action"""

        if self.action == 'create':
            return CreateRideSerializer

        return RideModelSerializer

    def get_queryset(self):
        """Manages getting the queryset."""

        circle = self.circle
        offset = timezone.now() + timedelta(minutes=30)

        queryset = circle.ride_set.filter(
            available_seats__gte=1,
            departure_date__gte=offset
        )

        return queryset
