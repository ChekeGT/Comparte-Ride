"""Qualification model related serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from cride.rides.models import Qualification

# Serializers
from cride.users.serializers import UserModelSerializer


class QualificationModelSerializer(serializers.ModelSerializer):

    user = UserModelSerializer()

    class Meta:
        """Metadata class."""

        model = Qualification
        fields = ('user', 'score')
