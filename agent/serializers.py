from rest_framework import serializers
from .models import DetectedSound
from core.models import SoundCategory

class DetectedSoundSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=SoundCategory.objects.all())
    category_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DetectedSound
        fields = [
            'id', 'user', 'sound_type', 'category', 'category_detail', 'confidence',
            'timestamp', 'transcription', 'raw_data', 'audio_path'
        ]
        read_only_fields = ['id', 'timestamp', 'user', 'category_detail']

    def get_category_detail(self, obj):
        if obj.category:
            return {
                'id': obj.category.id,
                'name': obj.category.name,
                'label': obj.category.label,
                'emoji': obj.category.emoji,
            }
        return None 