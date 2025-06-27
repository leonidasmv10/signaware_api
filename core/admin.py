from django.contrib import admin
from .models import VehicleType, SoundType

@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'description')
    search_fields = ('type_name',)

@admin.register(SoundType)
class SoundTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'description') 
    search_fields = ('type_name',) 