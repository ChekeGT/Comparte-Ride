"""Circles app urls configuration and mapping"""

# Django
from django.urls import path, include

# Django REST Framework
from rest_framework.routers import SimpleRouter

# Views
from .views import CircleModelViewSet, MembershipViewSet



app_name = 'Circles'

router = SimpleRouter()

# I dont gave anything in the regex parameter because i
# have already set it in the urls global file.
router.register(r'', CircleModelViewSet, base_name='circles')

router.register(
    r'(?P<slug_name>[^/.]+)/members',
    MembershipViewSet,
    base_name='membership'
)

urlpatterns = [
    path('', include(router.urls))
]
