from django.contrib import admin
from .models import VisualDetection, Location, AudioDetection

@admin.register(VisualDetection)
class VisualDetectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'vehicle_type', 'frequency', 'detection_date')
    list_filter = ('vehicle_type', 'detection_date')
    search_fields = ('user__username', 'vehicle_type__type_name')
    ordering = ('-detection_date',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'latitud', 'longitud', 'date')
    search_fields = ('user__username',)
    ordering = ('-date',)

@admin.register(AudioDetection)
class AudioDetectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'sound_type', 'location', 'detection_date')
    search_fields = ('user__username', 'sound_type__name')
    ordering = ('-detection_date',)