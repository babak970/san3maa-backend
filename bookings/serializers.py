from rest_framework import serializers
from django.utils.dateparse import parse_datetime

from .models import Booking
from arenas.models import Court


class BookingCreateSerializer(serializers.Serializer):
    court_id = serializers.IntegerField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

    def validate(self, data):
        if data["end"] <= data["start"]:
            raise serializers.ValidationError("end must be after start")
        return data


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["id", "user", "court", "start", "end", "price", "status", "created_at"]
        read_only_fields = fields
