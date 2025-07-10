from django.contrib import admin
from .models import DetectedSound

@admin.register(DetectedSound)
class DetectedSoundAdmin(admin.ModelAdmin):
    list_display = ('sound_type', 'category', 'confidence', 'timestamp', 'user')
    list_filter = ('category', 'timestamp', 'user')
    search_fields = ('sound_type', 'transcription')
