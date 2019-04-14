"""Circles Model related Serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from cride.circles.models import Circle


class CircleModelSerializer(serializers.ModelSerializer):
    """Circle Model serializer."""

    members_limit = serializers.IntegerField(
        required=False,
        min_value=10
    )

    is_limited = serializers.BooleanField(
        default=False
    )

    def validate(self, data):
        """Verifies congruence between is_limited and members_limit fields."""

        method = self.context['request'].method

        if method == 'POST':
            members_limit = data.get('members_limit', None)
            is_limited = data.get('is_limited', False)

            if bool(members_limit) ^ is_limited:
                raise serializers.ValidationError('If there is members_limit or is_limited both need to exist.')

        return data

    class Meta:
        """Metadata Class."""

        model = Circle

        fields = (
            'name', 'slug_name', 'about', 'picture', 'rides_offered',
            'rides_taken', 'is_verified', 'is_public', 'is_limited', 'members_limit'
        )

        read_only_fields = (
            'is_public', 'is_verified',
            'rides_offered', 'rides_taken'
        )
