"""Circles app views module."""

# Django REST Framework
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Models
from .models import Circle

# Serializers
from .serializers import CircleSerializer, CreateCircleSerializer


@api_view(['GET'])
def list_circles(request):
    """Api view that list all the public circles."""
    circles = Circle.objects.filter(is_public=True)
    serializer = CircleSerializer(circles, many=True)
    data = serializer.data
    return Response(data, status=200)


@api_view(['POST'])
def create_circle(request):
    """Api view for creating a circle."""
    serializer = CreateCircleSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        data = serializer.data
        circle = serializer.save(data)

        serialized_circle = CircleSerializer(circle)

        return Response(serialized_circle.data)
