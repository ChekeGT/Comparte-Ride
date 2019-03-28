"""Circles Model related views."""

# Django REST Framework
from rest_framework.viewsets import  GenericViewSet

# Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions import  IsCircleAdmin

# Mixins
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    ListModelMixin
)

# Models
from cride.circles.models import Circle, Membership

# Serializers
from cride.circles.serializers import CircleModelSerializer

class CircleModelViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin, GenericViewSet):
    """Circle Model View Set. Manages Every API View related with Circle Model."""

    serializer_class = CircleModelSerializer
    lookup_field = 'slug_name'

    def get_queryset(self):
        """Returns filtered queryset."""

        queryset = Circle.objects.all()

        if self.action == 'list':
            queryset = queryset.filter(is_public=True)

        return queryset

    def get_permissions(self):
        permission_classes = [IsAuthenticated(),]

        if self.action in ['update', 'partial_update']:
            permission_classes.append(IsCircleAdmin())

        return permission_classes

    def perform_create(self, serializer):
        """Ensures user is creating the Circle became in the admin of this."""

        circle = serializer.save()
        user = self.request.user

        Membership.objects.create(
            user=user,
            circle=circle,
            is_admin=True,
            remaining_invitations=20
        )
