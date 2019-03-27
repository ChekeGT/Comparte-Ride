"""Login Serializer file."""

# Django REST Framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token

# Django
from django.contrib.auth import authenticate

# Models
from cride.users.models import User


class UserLoginSerializer(serializers.Serializer):
    """Handles and validate the data when a user tries to login."""

    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)


    def validate(self, data):
        """Checks credentials."""

        email = data['email']
        password = data['password']

        user = authenticate(
            username=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError('Invalid Credentials.')

        self.context['user'] = user
        return data

    def create(self, validated_data):
        """Generate or retrieve a new token."""

        user = self.context['user']
        token, created = Token.objects.get_or_create(user=user)

        return (user, token.key)


class UserModelSerializer(serializers.ModelSerializer):
    """Serializer of the user model."""

    class Meta:
        """Metadata configurations."""

        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number'
        )
