"""Circles Model related views."""

# Django REST Framework
from rest_framework.viewsets import  ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

# Models
from cride.circles.models import Circle

# Serializers
from cride.circles.serializers import CircleModelSerializer

class CircleModelViewSet(ModelViewSet):
    """Circle Model View Set. Manages Every API View related with Circle Model."""

    serializer_class = CircleModelSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Returns filtered queryset."""

        queryset = Circle.objects.all()

        if self.action == 'list':
            queryset = queryset.filter(is_public=True)

        return queryset

