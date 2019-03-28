"""File that contains the login view."""

# Django REST Framework
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

# Mixins
from rest_framework.mixins import  RetrieveModelMixin

# Serializers
from cride.users.serializers import (
    UserLoginSerializer,
    UserModelSerializer,
    UserSignupSerializer,
    UserVerifySerializer,
)
from cride.circles.serializers import CircleModelSerializer

# Models
from cride.users.models import User
from cride.circles.models import Circle

# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from cride.users.permissions import IsAccountOwner


class UserManagementViewSet(RetrieveModelMixin, GenericViewSet):
    """Manages all views related to the user model."""

    queryset = User.objects.filter(is_verified=True, is_client=True)
    lookup_field = 'username'
    serializer_class = UserModelSerializer

    def get_permissions(self):
        """Returns the permissions depending on the action."""
        if self.action in ['login', 'signup', 'verify']:
            permissions = [AllowAny()]
        elif self.action == 'retrieve':
            permissions = [IsAuthenticated(), IsAccountOwner()]
        else:
            permissions = [IsAuthenticated()]
        return permissions

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Manages the login of a user."""

        login = UserLoginSerializer(data=request.data)

        if login.is_valid(raise_exception=True):
            user, token = login.save()
            response = {
                'user': UserModelSerializer(user).data,
                'access_token': token
            }
            return Response(response, status=HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def signup(self, request):
        """ Manages the signup of a user."""

        signup = UserSignupSerializer(data=request.data)

        if signup.is_valid(raise_exception=True):
            user = signup.save()
            response = user.data

            return Response(response, status=HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Manages the verification of a user."""

        serializer = UserVerifySerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            data = {
                'message': 'Your account is now verified, start taking some Rides!'
            }

            return Response(data, status=HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """Add extra data(Circles in which the user is member.) to the response."""

        response = super(UserManagementViewSet, self).retrieve(request, args, kwargs)

        circles = Circle.objects.filter(
            members=request.user,
            membership__is_active=True
        )
        data = {
            'user': response.data,
            'circles': CircleModelSerializer(circles, many=True).data
        }
        response.data = data

        return response
