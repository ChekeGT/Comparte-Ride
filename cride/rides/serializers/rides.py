"""Rides Model Related Serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from cride.rides.models import Ride
from cride.circles.models import Membership

# Utilities
from django.utils import timezone
from datetime import timedelta


class CreateRideSerializer(serializers.ModelSerializer):

    offered_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault(
        )
    )

    available_seats = serializers.IntegerField(min_value=1, max_value=10)

    class Meta:
        """Metadata class."""

        model = Ride

        exclude = (
            'rating', 'passengers',
            'is_active', 'offered_in'
        )

    def validate_departure_date(self, departure_date):
        """Handles checking date is'nt to late to response to it."""

        min_date = timezone.now() + timedelta(minutes=30)

        if departure_date < min_date:
            raise serializers.ValidationError(
                'Departure time must be at least the next 30 minutes window.'
            )

        return departure_date

    def validate(self, data):
        """Validate

        Verify that the person who offers the ride is member,
        the same user making the request
        and also the departure_date is'nt less than arrival_date.
        """

        user = data['offered_by']
        circle = self.context['circle']
        arrival_date = data['arrival_date']
        departure_date = data['departure_date']

        # Validates user is member of the circle
        try:
            membership = Membership.objects.get(
                user=user,
                circle=circle,
                is_active=True
            )

        except Membership.DoesNotExist:
            raise serializers.ValidationError(f'This user is not a member of the circle {circle.name}')

        else:
            self.context['membership'] = membership

        # Validates the request user is the same given in the data.

        if self.context['request'].user != user:
            raise serializers.ValidationError('Rides offered on behalf of others are not allowed.')

        # Validates the dates.

        if arrival_date <= departure_date:
            raise serializers.ValidationError('Departure date must be after arrival date.')

        return data

    def create(self, validated_data):
        """Create ride and update stats."""

        circle = self.context['circle']
        membership = self.context['membership']
        profile = validated_data['offered_by'].profile

        ride = Ride.objects.create(
            offered_in=circle,
            **validated_data
        )

        # Updating data
        circle.rides_offered += 1
        circle.save()

        membership.rides_offered += 1
        membership.save()

        profile.rides_offered += 1
        profile.save()

        return ride
