from django.db import models
from django.conf import settings
from core.models import SoundCategory

# Create your models here.

class DetectedSound(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='detected_sounds')
    sound_type = models.CharField(max_length=100)  # Ej: Speech, Siren, etc.
    category = models.ForeignKey(SoundCategory, on_delete=models.PROTECT, related_name='detected_sounds')
    confidence = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    transcription = models.TextField(blank=True, null=True)
    raw_data = models.JSONField(blank=True, null=True)
    audio_path = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.sound_type} ({self.category}) - {self.timestamp:%Y-%m-%d %H:%M:%S}"
