from rest_framework import serializers
from .models import DrivingHistory

class DrivingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DrivingHistory
        fields = '__all__'
        read_only_fields = ['user', 'registration_date']
