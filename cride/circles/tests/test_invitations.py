"""Invitation model related tests."""

# Django
from django.test import TestCase
from django.shortcuts import reverse

# Django REST Framework
from rest_framework.test import APITestCase

# Models
from cride.users.models import (
    User,
    Profile
)
from cride.circles.models import (
    Circle,
    Invitation,
    Membership
)
from rest_framework.authtoken.models import (
    Token
)

# Status
from rest_framework.status import (
    HTTP_200_OK
)


class InvitationTestCase(TestCase):
    """Class that manages every test related to the invitation model."""

    def setUp(self):
        """Manages seting up the test case class."""

        self.user = User.objects.create_user(
            first_name='Francisco',
            last_name='Ramirez',
            username='cheke',
            email='c@a.com',
            password='cheke12345678cheke',
            is_verified=True
        )
        self.circle = Circle.objects.create(
            name='Facultad de filosofia y letras',
            slug_name='F&L-Unam',
            about='Grupo oficial de la facultutad de filosofia y letras de la unam.',
            is_verified=True
        )

    def test_code_generation(self):
        """Random codes should be generated automatically."""

        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
        )
        return self.assertIsNotNone(
            invitation.code
        )

    def test_code_usage(self):
        """If a code is given, there is no need to create a new one"""

        code = 'unam_special_code'

        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
            code=code
        )
        return self.assertEqual(
            code,
            invitation.code
        )

    def test_code_generation_if_duplicated(self):
        """Random codes should be generated if the given code is already used."""

        code = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle
        ).code

        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
            code=code
        )
        return self.assertNotEqual(
            code,
            invitation.code
        )


class InvitationApiEndPoint(APITestCase):
    """Manages testing of the invitation related api views."""

    def setUp(self):
        """Handles setting up all the data."""

        # Models
        self.user = User.objects.create_user(
            first_name='Francisco',
            last_name='Ramirez',
            username='cheke',
            email='c@a.com',
            password='cheke12345678cheke',
            is_verified=True
        )
        self.profile = Profile.objects.create(
            user=self.user
        )
        self.circle = Circle.objects.create(
            name='Facultad de filosofia y letras',
            slug_name='F&L-Unam',
            about='Grupo oficial de la facultutad de filosofia y letras de la unam.',
            is_verified=True
        )
        self.membership = Membership.objects.create(
            user=self.user,
            circle=self.circle,
            remaining_invitations=100
        )

        # Url
        self.url = reverse(
            'circles:membership-invitations',
            args=[
                self.circle.slug_name,
                self.user.username
            ]
        )

        # Authentication
        self.access_token = Token.objects.create(
            user=self.user
        ).key

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.access_token}')

    def test_request_success(self):
        """Checks the status code of the request is equal to 200"""

        request = self.client.get(
            self.url
        )

        return self.assertEqual(request.status_code, HTTP_200_OK)

    def test_invitation_creation(self):
        """Verify invitation are generated if none exist previously"""

        # Invitations in db must be 0

        self.assertEqual(Invitation.objects.count(), 0)

        # Call invitations end point
        request = self.client.get(
            self.url
        )
        self.assertEqual(request.status_code, HTTP_200_OK)

        # Verify new invitations were created

        invitations = Invitation.objects.filter(
            issued_by=self.user
        )
        self.assertEqual(invitations.count(), 100)

        for invitation in invitations:
            self.assertIn(invitation.code, request.data['unused_invitations'])
