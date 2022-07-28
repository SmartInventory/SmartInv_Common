from django.utils import timezone
from rest_framework import serializers


def no_past(value):
    if value < timezone.now():
        raise serializers.ValidationError("error.booking.end_date")
