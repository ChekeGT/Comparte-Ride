"""File that contains the login view."""

# Django REST Framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

# Serializers
from cride.users.serializers import (
    UserLoginSerializer,
    UserModelSerializer,
    UserSignupSerializer
)


class UserLoginAPIView(APIView):
    """Api view, manages the login of a user."""

    def post(self, request):
        """What to do when te method called is post.

        Manages the login of a user.
        """

        login = UserLoginSerializer(data=request.data)

        if login.is_valid(raise_exception=True):
            user, token = login.save()
            response = {
                'user': UserModelSerializer(user).data,
                'access_token': token
            }
            return Response(response, status=HTTP_201_CREATED)



class UserSignupAPIView(APIView):
    """Api view, manages the signup of a user."""

    def post(self, request):
        """What to do when te method called is POST.

        Manages the signup of a user.
        """

        signup = UserSignupSerializer(data=request.data)

        if signup.is_valid(raise_exception=True):
            user = signup.save()
            response  = user.data

            return Response(response, status=HTTP_201_CREATED)
