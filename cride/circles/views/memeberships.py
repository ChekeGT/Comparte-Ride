"""Membership model related views."""

# Django REST Framework
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    CreateModelMixin
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

# Models
from cride.circles.models import (
    Circle,
    Membership,
    Invitation
)

# Serializers
from cride.circles.serializers import MembershipModelSerializer, AddMemberSerializer

# Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions import (
    IsCircleActiveMember,
    IsAdminOrMembershipOwner,
    IsMembershipOwner
)

# Status
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED
)


class MembershipViewSet(
    ListModelMixin,
    GenericViewSet,
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):
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

        if self.action == 'invitations':
            permissions.append(
                IsMembershipOwner()
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

    @action(detail=True, methods=['get'])
    def invitations(self, request, *args, **kwargs):
        """Retrieve a member's invitation breakdown.

        Will return a list containing all the members that have
        used it's invitations and another list containing the
        invitations that have'nt be used yet.
        """

        membership = self.get_object()

        invited_members = Membership.objects.filter(
            invited_by=request.user,
            circle=self.circle,
            is_active=True
        )

        for remaining_invitation in range(membership.remaining_invitations):
            Invitation.objects.create(
                issued_by=request.user,
                circle=self.circle,
            )

        membership.remaining_invitations = 0
        membership.save()

        unused_invitations = [
            x[0] for x in Invitation.objects.filter(
                issued_by=request.user,
                circle=self.circle,
                used=False
            ).values_list('code')
        ]

        data = {
            'used_invitations': MembershipModelSerializer(invited_members, many=True).data,
            'unused_invitations': unused_invitations
        }

        return Response(data=data, status=HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Handle member creation from invitation code."""

        serializer = AddMemberSerializer(
            data=request.data,
            context={
                'circle': self.circle,
                'request': request
            }
        )

        if serializer.is_valid(raise_exception=True):

            member = serializer.save()

            data = self.get_serializer(member).data

            return Response(data=data, status=HTTP_201_CREATED)
