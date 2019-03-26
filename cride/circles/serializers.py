"""Circles app serializers module."""

# Django REST Framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# Models
from .models import Circle


class CircleSerializer(serializers.Serializer):
    """Circle model serializer."""

    name = serializers.CharField()
    slug_name = serializers.SlugField()

    rides_taken = serializers.IntegerField()
    rides_offered = serializers.IntegerField()

    members_limit = serializers.IntegerField()



class CreateCircleSerializer(serializers.Serializer):
    """Serializer used for creating a Circle."""

    name = serializers.CharField(
        max_length=140
    )
    slug_name = serializers.SlugField(
        max_length=40,
        validators=[
            UniqueValidator(
                Circle.objects.all()
            )
        ]
    )

    about = serializers.CharField(
        max_length=255,
        required=False
    )

    def save(self, data):
        """Creates and returns a circle with some data."""
        return Circle.objects.create(**data)
