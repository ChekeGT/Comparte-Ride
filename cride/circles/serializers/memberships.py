"""Membership model related serializers."""

# Django REST Framework
from rest_framework import serializers

# Serializers
from cride.users.serializers import UserModelSerializer

# Models
from cride.circles.models import Membership


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
