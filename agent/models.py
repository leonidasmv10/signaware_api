from django.db import models
from django.conf import settings
from core.models import SoundCategory, SoundType

# Create your models here.

class DetectedSound(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='detected_sounds')
    sound_type = models.ForeignKey(SoundType, on_delete=models.PROTECT, related_name='detected_sounds')
    category = models.ForeignKey(SoundCategory, on_delete=models.PROTECT, related_name='detected_sounds')
    confidence = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    transcription = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.sound_type} ({self.category}) - {self.timestamp:%Y-%m-%d %H:%M:%S}"

    class Meta:
        ordering = ['-timestamp']
