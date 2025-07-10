from rest_framework import serializers
from .models import SoundCategory

class SoundCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SoundCategory
        fields = '__all__'