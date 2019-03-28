"""Login Serializer file."""

# Django REST Framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token

# Django
from django.contrib.auth import authenticate, password_validation
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

# Models
from cride.users.models import User, Profile

# Validators
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator

# JWT
import jwt

# Utilities
from datetime import timedelta
from django.utils import timezone

# Settings
from django.conf import settings


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

        if not user.is_verified:
            raise serializers.ValidationError("This user is'nt verified yet.")

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

        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user)

        self.send_confirmation_email(user)

        return UserModelSerializer(user)

    def send_confirmation_email(self, user):
        """Send account verification email to a given user."""

        verification_token = self.generate_verification_token(user)
        subject = f'Welcome @{user.username}! Verify your account to start using Comparte Ride'
        from_email = 'Comparte Ride <noreply@comparteride.com>'
        content = render_to_string(
            'emails/users/account_verification.html',
            {
                'token': verification_token,
                'user': user,
                'dns': settings.ALLOWED_HOSTS[0]
            }
        )
        msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
        msg.attach_alternative(content, "text/html")
        msg.send()

    def generate_verification_token(self, user):
        """Create JWT that the user can use to verify it's acount."""

        expiration_date = timezone.now() + timedelta(days=3)

        payload = {
            'user': user.username,
            'exp': expiration_date.timestamp(),
            'type': 'email_confirmation'
        }

        # This could be a little bit confusing, why are we decoding this?
        # Well, the function jwt.encode returns a byte object so to parse
        # it to a string we need to use the method decode, but we are not
        # decoding the JWT, just passing the byte object to str.
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').decode()

        return token


class UserVerifySerializer(serializers.Serializer):
    """Handles the data when a user is trying to verify it's account."""

    token = serializers.CharField()

    def validate_token(self, token):
        """Verifies the token is valid."""

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            type = payload['type']

            if type != 'email_confirmation':
                raise jwt.PyJWTError

        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('The validation time has expired.')

        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token.')

        else:

            self.context['payload'] = payload

            return token

    def validate(self, data):
        """Verifies the user have'nt verified it's account yet."""

        payload = self.context['payload']
        username = payload['user']

        if User.objects.filter(username=username, is_verified=True).exists():
            raise serializers.ValidationError('You have already verified your email.')

        return data

    def save(self):
        """Makes the field is_verified of the user True(Only if the token was valid)."""

        payload = self.context['payload']
        username = payload['user']

        user = User.objects.get(username=username)
        user.is_verified = True
        user.save()
