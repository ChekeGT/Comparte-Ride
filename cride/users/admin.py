"""Admin of Users App Configuration."""

# Django
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin

# Models
from cride.users.models import Profile, User


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_client')
    list_filter = ('is_client', 'is_staff', 'created', 'modified')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Profile Model Admin."""

    list_display = ('user', 'rides_taken', 'rides_offered', 'reputation')
    list_filter = ('reputation',)
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')


admin.site.register(User, UserAdmin)
