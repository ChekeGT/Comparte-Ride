"""Circles model related permissions."""

# Django REST Framework
from rest_framework.permissions import BasePermission

# Models
from cride.circles.models import Membership


class IsCircleAdmin(BasePermission):
    """Allow access only to cirlce admins."""

    def has_object_permission(self, request, view, circle):
        """Verifies the user calling this function is admin of the circle."""
        user = request.user

        if Membership.objects.filter(user=user, circle=circle, is_admin=True, is_active=True).exists():
            return True
        else:
            return False
