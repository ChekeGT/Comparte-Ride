"""Membership model related serializers."""

# Django REST Framework
from rest_framework import serializers

# Serializers
from cride.users.serializers import UserModelSerializer

# Models
from cride.circles.models import Membership, Invitation

# Utilites
from django.utils import timezone


class MembershipModelSerializer(serializers.ModelSerializer):
    """Membership Model Serializer"""

    joined_at = serializers.DateTimeField(source='created', read_only=True)

    user =  UserModelSerializer(read_only=True)
    invited_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        """Metadata class."""

        model = Membership

        fields = (
            'user', 'is_admin', 'is_active',
            # Invitations
            'used_invitations', 'remaining_invitations',
            'invited_by',
            # Stats
            'rides_taken', 'rides_offered',
            'joined_at'
        )

        read_only_fields = (
            'user',
            'used_invitations',
            'remaining_invitations',
            'invited_by',
            'rides_taken',
            'rides_offered'
        )


class AddMemberSerializer(serializers.Serializer):
    """Add Member Serializer

    Handle the addition of a new member to a circle.
    Circle object must be provided in the context.
    """

    invitation_code = serializers.CharField(min_length=50, max_length=50)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_user(self, user):
        """Verify is'nt already a member."""

        circle = self.context['circle']

        query = Membership.objects.filter(
            user=user,
            circle=circle,
        )

        if query.exists():
            raise serializers.ValidationError('The user is already a member.')

        return user

    def validate_invitation_code(self, invitation_code):
        """Verify code exists and its related to the circle."""

        try:
            circle = self.context['circle']

            invitation = Invitation.objects.get(
                code=invitation_code,
                circle=circle,
                used=False
            )

        except Invitation.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation code")

        else:
            self.context['invitation'] = invitation
            return invitation_code

    def validate(self, data):
        """Verify circle is capable of accepting new members."""

        circle = self.context['circle']

        if circle.is_limited and circle.members.count >= circle.members_limit:
            raise serializers.ValidationError("Circle has reached it's member limit")

        return data

    def create(self, validated_data):
        """Create new circle member."""

        circle = self.context['circle']
        invitation = self.context['invitation']

        user = validated_data['user']

        now = timezone.now()

        member = Membership.objects.create(
            user=user,
            circle=circle,
            invited_by=invitation.issued_by,
        )

        invitation.used_by = user
        invitation.used_at = now
        invitation.used = True
        invitation.save()

        # Update Issuer Data
        issuer = Membership.objects.get(
            user=invitation.issued_by,
            circle=circle
        )
        issuer.used_invitations += 1
        issuer.save()
        return member
