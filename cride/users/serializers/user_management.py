"""Login Serializer file."""

# Django REST Framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token

# Django
from django.contrib.auth import authenticate, password_validation

# Models
from cride.users.models import User, Profile

# Validators
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator


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


class UserSignupSerializer(serializers.Serializer):
    """Handles and validates te data when a user signs up."""

    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    username = serializers.CharField(
        min_length=4,
        max_length=20,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    # Phone number
    PHONE_REGEX_VALIDATOR = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message='Phone number must be entered in the format: +999999999. Up to 15 digits allowed.'
    )
    phone_number = serializers.CharField(
        validators=[
            PHONE_REGEX_VALIDATOR
        ]
    )

    # Password
    password = serializers.CharField(
        min_length=8
    )
    password_confirmation = serializers.CharField(
        min_length=8
    )

    # Name
    first_name = serializers.CharField(
        max_length=50
    )
    last_name = serializers.CharField(
        max_length=50
    )

    def validate(self, data):
        """ Makes verifications to the password field.

        Verifications:
            Verifies password matches with password_confirmation.
            Verifies password is valid using Django's validations.
        """

        password = data['password']
        password_confirmation = data['password_confirmation']

        if password != password_confirmation:
            raise serializers.ValidationError("Passwords does'nt match.")

        data.pop('password_confirmation')
        password_validation.validate_password(password)

        return data

    def create(self, validated_data):
        """Creates user and profile when the data is validated."""

        user = User.objects.create(**validated_data)
        profile = Profile.objects.create(user=user)

        return UserModelSerializer(user)
