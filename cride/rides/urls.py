"""Rides app urls configuration and mapping"""

# Django
from django.urls import path, include

# Django REST Framework
from rest_framework.routers import SimpleRouter

# Views
from .views import RideViewSet

app_name = 'Rides'

router = SimpleRouter()

# I dont gave anything in the regex parameter because i
# have already set it in the urls global file.
router.register(
    r'(?P<slug_name>[^/.]+)/rides',
    RideViewSet,
    base_name='ride'
)

urlpatterns = [
    path('', include(router.urls))
]
