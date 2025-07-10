from django.contrib import admin
from .models import DetectedSound
# from core.models import SoundType

# @admin.register(SoundType)
# class SoundTypeAdmin(admin.ModelAdmin):
#     list_display = ('name', 'label', 'is_critical', 'created_at')
#     list_filter = ('is_critical', 'created_at')
#     search_fields = ('name', 'label', 'description')
#     ordering = ('name',)

@admin.register(DetectedSound)
class DetectedSoundAdmin(admin.ModelAdmin):
    list_display = ('sound_type', 'category', 'confidence', 'timestamp', 'user')
    list_filter = ('sound_type', 'category', 'timestamp', 'user')
    search_fields = ('sound_type__name', 'sound_type__label', 'transcription')
