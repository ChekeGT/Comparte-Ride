"""Membership model related views."""

# Django REST Framework
from rest_framework.mixins import (
    ListModelMixin,

)
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import get_object_or_404

# Models
from cride.circles.models import Circle, Membership

# Serializers
from cride.circles.serializers import MembershipModelSerializer

class MembershipViewSet(ListModelMixin, GenericViewSet):
    """"Circle Membership View Set."""

    serializer_class = MembershipModelSerializer

    def dispatch(self, request, *args, **kwargs):
        """Return the normal dispatch but adds the circle model."""
        slug_name = kwargs['slug_name']
        self.circle = get_object_or_404(Circle, slug_name=slug_name)
        
        return super(MembershipViewSet, self).dispatch(request, args, kwargs)

    def get_queryset(self):
        """Gets the members of the circle."""

        return Membership.objects.filter(
            is_active=True,
            circle=self.circle
        )
