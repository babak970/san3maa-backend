# arenas/serializers.py
from rest_framework import serializers
from .models import Arena, Court


class CourtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = ['id', 'arena', 'name', 'sport_type', 'capacity', 'indoor']


class ArenaSerializer(serializers.ModelSerializer):
    # show related courts as nested read-only list
    courts = CourtSerializer(many=True, read_only=True)

    class Meta:
        model = Arena
        fields = [
            'id',
            'owner',
            'name',
            'address',
            'latitude',
            'longitude',
            'is_active',
            'courts',
        ]
