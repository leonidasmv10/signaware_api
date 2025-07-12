from django.contrib import admin
from .models import DetectedSound

@admin.register(DetectedSound)
class DetectedSoundAdmin(admin.ModelAdmin):
    list_display = ('sound_type', 'category', 'confidence', 'timestamp', 'user')
    list_filter = ('sound_type', 'category', 'timestamp', 'user')
    search_fields = ('sound_type__name', 'sound_type__label', 'transcription')
