"""Membership model related views."""

# Django REST Framework
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import get_object_or_404

# Models
from cride.circles.models import Circle, Membership

# Serializers
from cride.circles.serializers import MembershipModelSerializer

# Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions import (
    IsCircleActiveMember,
    IsAdminOrMembershipOwner
)


class MembershipViewSet(
    ListModelMixin,
    GenericViewSet,
    RetrieveModelMixin,
    DestroyModelMixin):
    """"Circle Membership View Set."""

    serializer_class = MembershipModelSerializer
    lookup_field = 'username'

    def dispatch(self, request, *args, **kwargs):
        """Return the normal dispatch but adds the circle model."""
        slug_name = kwargs['slug_name']
        self.circle = get_object_or_404(Circle, slug_name=slug_name)

        return super(MembershipViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Modifies the default permission classes."""

        permissions = [IsAuthenticated(), IsCircleActiveMember()]

        if self.action == 'destroy':
            permissions.append(
                IsAdminOrMembershipOwner()
            )

        return permissions

    def get_queryset(self):
        """Gets the members of the circle."""

        return Membership.objects.filter(
            is_active=True,
            circle=self.circle
        )

    def get_object(self):
        """Returns the membership of the request user."""

        return get_object_or_404(
            Membership,
            user__username=self.kwargs['username'],
            circle=self.circle,
            is_active=True
        )

    def perform_destroy(self, instance):
        """Deactivates the membership and does'nt delete it."""
        instance.is_active = False
        instance.save()
