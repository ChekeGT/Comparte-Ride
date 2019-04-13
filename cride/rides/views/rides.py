"""Ride Model Related views."""

# Django REST Framework
from rest_framework.decorators import action
from rest_framework.response import Response

# Mixins
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    UpdateModelMixin
)
from cride.utils.mixins import AddCircleMixin

# Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions import IsCircleActiveMember
from cride.rides.permissions import (
    IsRideOwner,
    IsNotRideOwner
)

# Serializers
from cride.rides.serializers import (
    CreateRideSerializer,
    RideModelSerializer,
    JoinRideSerializer,
    EndRideSerializer,
    QualifyRideSerializer
)

# Utilities
from django.utils import timezone
from datetime import timedelta

# Filters
from rest_framework.filters import SearchFilter, OrderingFilter

# Status
from rest_framework.status import (
    HTTP_200_OK
)


class RideViewSet(
    AddCircleMixin,
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin
):
    """Manages CRUD of Ride model."""

    filter_backends = (SearchFilter, OrderingFilter)

    search_fields = ('departure_location', 'arrival_location')

    ordering_fields = ('departure_date', 'arrival_date', 'available_seats')

    ordering = ('departure_date', 'arrival_date', 'available_seats')

    def get_serializer_context(self):
        """Modifies the serializer context adding the current circle to the context."""

        context = super(RideViewSet, self).get_serializer_context()

        context['circle'] = self.circle

        if self.action in ['join', 'finish', 'qualify']:
            context['ride'] = self.get_object()

        return context

    def get_serializer_class(self):
        """Returns serializer class based on action"""

        if self.action == 'create':
            return CreateRideSerializer

        if self.action == 'join':
            return JoinRideSerializer

        if self.action == 'finish':
            return EndRideSerializer

        if self.action == 'qualify':
            return QualifyRideSerializer

        return RideModelSerializer

    def get_queryset(self):
        """Manages getting the queryset."""

        circle = self.circle

        if not self.action in ['finish', 'qualify']:
            offset = timezone.now() + timedelta(minutes=10)

            queryset = circle.ride_set.filter(
                available_seats__gte=1,
                departure_date__gte=offset
            )
        else:
            queryset = circle.ride_set.all()

        return queryset

    def get_permissions(self):
        """Returns permissions based on action."""

        permissions = [
            IsAuthenticated(),
            IsCircleActiveMember(),
        ]

        if self.action in ['update', 'partial_update', 'finish']:
            permissions.append(
                IsRideOwner()
            )

        if self.action in ['join', 'qualify']:
            permissions.append(
                IsNotRideOwner()
            )

        return permissions

    @action(detail=True, methods=['post'])
    def join(self, request, *args, **kwargs):
        """Handles joining to a circle."""

        ride = self.get_object()

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            ride,
            data={
                'passenger': request.user.pk
            },
            context=self.get_serializer_context(),
            partial=True
        )

        if serializer.is_valid(raise_exception=True):
            ride = serializer.save()
            data = RideModelSerializer(ride).data

            return Response(data=data, status=HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def finish(self, request, *args, **kwargs):
        """Handles finishing a ride."""

        ride = self.get_object()

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            ride,
            data={
                'is_active': False,
                'current_time': timezone.now()
            },
            context=self.get_serializer_context(),
            partial=True
        )

        if serializer.is_valid(raise_exception=True):
            ride = serializer.save()

            data = RideModelSerializer(ride).data

            return Response(data=data, status=HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def qualify(self, request, *args, **kwargs):
        """Manages giving qualification to a ride"""

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            data=request.data,
            context=self.get_serializer_context(),
        )

        if serializer.is_valid(raise_exception=True):
            ride = serializer.save()

            data = RideModelSerializer(ride).data

            return Response(data=data, status=HTTP_200_OK)

