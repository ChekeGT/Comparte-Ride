"""Ride model related permissions."""

# Django REST Framework
from rest_framework.permissions import BasePermission


class IsRideOwner(BasePermission):
    """Verifies the request user is the same as ride creator."""

    def has_object_permission(self, request, view, obj):
        """Returns if the request user is the same as ride creator."""

        return request.user == obj.offered_by
