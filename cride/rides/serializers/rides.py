
"""Rides Model Related Serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from cride.rides.models import (
    Ride,
    Qualification
)
from cride.circles.models import Membership
from cride.users.models import User

# Utilities
from django.utils import timezone
from datetime import timedelta
from statistics import mean

# Serializers
from cride.users.serializers import UserModelSerializer
from .qualifications import QualificationModelSerializer


class RideModelSerializer(serializers.ModelSerializer):
    """Ride Model Serializer."""

    offered_by = UserModelSerializer(read_only=True)
    offered_in = serializers.StringRelatedField(read_only=True)

    passengers = UserModelSerializer(read_only=True, many=True)

    rating = QualificationModelSerializer(read_only=True, many=True)

    class Meta:
        """Metadata class."""

        model = Ride

        fields = '__all__'

        read_only_fields = (
            'rating', 'offered_by',
            'offered_in'
        )

    def update(self, instance, validated_data):
        """Handles validate the update is valid yet."""

        now = timezone.now()

        if instance.departure_date <= now:
            raise serializers.ValidationError('On going rides can not be updated.')

        return super(RideModelSerializer, self).update(instance, validated_data)


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


class JoinRideSerializer(serializers.ModelSerializer):
    """Handles validating data and joining to a ride."""

    passenger = serializers.IntegerField()

    class Meta:
        model = Ride
        fields = ('passenger',)

    def validate_passenger(self, passenger_pk):
        """Handles validating that the passenger exists and is circle member."""

        circle = self.context['circle']

        user_set = User.objects.filter(pk=passenger_pk)
        if not user_set.exists():
            raise serializers.ValidationError('The user does not exists.')

        membership_set = Membership.objects.filter(user__pk=passenger_pk, circle=circle, is_active=True)

        if not membership_set.exists():
            raise serializers.ValidationError('This user is not member of this circle.')

        self.context['membership'] = membership_set.first()
        self.context['user'] = user_set.first()

        return passenger_pk

    def validate(self, data):
        """Handles validating the ride is accessible"""

        ride = self.context['ride']
        offset = timezone.now() + timedelta(minutes=10)
        user = self.context['user']

        if ride.departure_date <= offset:
            raise serializers.ValidationError('This ride is on going.')

        if user in ride.passengers.all():
            raise serializers.ValidationError('You are already in this ride.')

        if ride.available_seats < 1:
            raise serializers.ValidationError('This ride has not available seats.')

        if ride.is_active == False:
            raise serializers.ValidationError('This ride has already ended.')

        if user == ride.offered_by:
            raise serializers.ValidationError('You  are the ride creator.')

        return data

    def update(self, instance, validated_data):
        """Handles updating the ride passengers."""

        ride = self.context['ride']
        user = self.context['user']
        profile = user.profile
        circle = self.context['circle']
        membership = self.context['membership']

        ride.passengers.add(user)

        # Updating stats

        # Ride
        ride.available_seats -= 1
        ride.save()

        # Profile
        profile.rides_taken += 1
        profile.save()

        # Circle
        circle.rides_taken += 1
        circle.save()

        # Membership
        membership.rides_taken += 1
        membership.save()

        return ride

    def save(self, **kwargs):
        """Creates a qualification, and returns the base functionality."""

        user = self.context['user']
        ride = self.context['ride']

        qualification = Qualification.objects.create(
            user=user
        )

        ride.rating.add(qualification)

        return super(JoinRideSerializer, self).save(**kwargs)


class EndRideSerializer(serializers.ModelSerializer):
    """Handles finishing a ride and validating that action."""

    current_time = serializers.DateTimeField()

    class Meta:
        """Metadata class."""

        model = Ride
        fields = ('is_active', 'current_time')

    def validate_current_time(self, current_time):
        """Handles validating that the current time is'nt before the ride"""

        ride = self.context['ride']

        if current_time < ride.departure_date:
            raise serializers.ValidationError("The ride have'nt started yet.")

        return current_time


class QualifyRideSerializer(serializers.Serializer):

    qualification = serializers.FloatField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_user(self, user):
        """Validate that:

        The user has not already given a rating
        The user is part of the ride
        """

        ride = self.context['ride']

        rating_set = ride.rating.all()

        user_rating = rating_set.get(user=user)

        rating_query = rating_set.filter(
            user=user,
            score__gt=0
        )

        if not user in ride.passengers.all():
            raise serializers.ValidationError('You are not in the ride.')

        if rating_query.exists():
            raise serializers.ValidationError('You already give a qualification to this ride.')

        self.context['rating'] = user_rating

        return user

    def validate_qualification(self, qualification):
        """Validates then qualification is greater then 0"""

        if qualification < 0:
            raise serializers.ValidationError('Qualification must be at least 0')

        if qualification > 5 or qualification  < 0:
            raise serializers.ValidationError('Qualification must be between 0 and 5')

        return qualification

    def validate(self, data):
        """Validates ride related things."""

        ride = self.context['ride']

        if ride.is_active:
            raise serializers.ValidationError("You could'nt qualify this ride until it did'nt ends.")

        return data

    def save(self, **kwargs):
        """Handles saving the ride."""

        rating = self.context['rating']

        rating.score = self.validated_data['qualification']

        rating.save()

        ride = self.context['ride']


        return ride
