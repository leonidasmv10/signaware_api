from rest_framework import serializers
from .models import VehicleType, SoundType

class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = '__all__'

class SoundTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoundType
        fields = '__all__'