from rest_framework import serializers
from .models import VisualDetection, Location, AudioDetection


class VisualDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisualDetection
        fields = ["id", "user", "vehicle_type", "frequency", "detection_date"]
        read_only_fields = ["user", "detection_date"]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "latitud", "longitud"]


class AudioDetectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = AudioDetection
        fields = ["sound_type", "location"]
