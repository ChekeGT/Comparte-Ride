"""Circles Model related Serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from cride.circles.models import Circle


class CircleModelSerializer(serializers.ModelSerializer):
    """Circle Model serializer."""

    class Meta:
        """Metadata Class."""

        model = Circle
        fields = (
            'name','slug_name','about','picture','rides_offered',
            'rides_taken','is_verified','is_public','is_limited','members_limit'
        )
