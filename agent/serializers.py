from rest_framework import serializers
from .models import DetectedSound
from core.models import SoundCategory, SoundType

class SoundTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoundType
        fields = ['id', 'name', 'label', 'description', 'is_critical']

class DetectedSoundSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    sound_type = serializers.PrimaryKeyRelatedField(queryset=SoundType.objects.all())
    sound_type_detail = serializers.SerializerMethodField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=SoundCategory.objects.all())
    category_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DetectedSound
        fields = [
            'id', 'user', 'sound_type', 'sound_type_detail', 'category', 'category_detail', 
            'confidence', 'timestamp', 'transcription'
        ]
        read_only_fields = ['id', 'timestamp', 'user', 'sound_type_detail', 'category_detail']

    def get_sound_type_detail(self, obj):
        if obj.sound_type:
            return {
                'id': obj.sound_type.id,
                'name': obj.sound_type.name,
                'label': obj.sound_type.label,
                'description': obj.sound_type.description,
                'is_critical': obj.sound_type.is_critical,
            }
        return None

    def get_category_detail(self, obj):
        if obj.category:
            return {
                'id': obj.category.id,
                'name': obj.category.name,
                'label': obj.category.label,
                'emoji': obj.category.emoji,
            }
        return None 