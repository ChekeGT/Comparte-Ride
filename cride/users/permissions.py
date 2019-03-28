"""User model related permission"""

# Django REST Framework
from rest_framework.permissions import BasePermission


class IsAccountOwner(BasePermission):
    """Only allow to use a view if the user calling it is the owner of the account."""

    def has_object_permission(self, request, view, user):
        """Returns if an user is owner of the account is trying to see"""

        return request.user == user
