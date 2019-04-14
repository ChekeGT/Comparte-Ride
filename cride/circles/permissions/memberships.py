"""Membership Model Related Permission Classes."""

# Django REST Framework
from rest_framework.permissions import BasePermission

# Models
from cride.circles.models import Membership


class IsCircleActiveMember(BasePermission):
    """Allow only active memberships.

    Expects the view already haves the circle
    in self.
    """

    def has_object_permission(self, request, view, obj):
        """Determines whether the user has an active membership within the circle"""

        try:
            Membership.objects.get(
                user=request.user,
                circle=view.circle,
                is_active=True
            )

        except Membership.DoesNotExist:
            return False

        else:
            return True


class IsAdminOrMembershipOwner(BasePermission):
    """Allow only admins or membership owners

    Permission used when deleting an account
    from a circle.
    """

    def has_object_permission(self, request, view, obj):
        """Determines if the user is admin or is the membership owner"""

        if request.user == obj.user:
            return True

        try:
            Membership.objects.get(
                user=request.user,
                circle=view.circle,
                is_active=True,
                is_admin=True
            )
        except Membership.DoesNotExist:
            return False

        else:
            return True


class IsMembershipOwner(BasePermission):
    """Allow only the membership owners to do some action."""

    def has_permission(self, request, view):
        """Let object permission grant access."""
        obj = view.get_object()

        return self.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        """Determines if the request user is the membership owner."""

        return request.user == obj.user
