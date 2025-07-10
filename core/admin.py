from django.contrib import admin
from .models import SoundCategory, SoundType

@admin.register(SoundCategory)
class SoundCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'label', 'emoji', 'is_critical')
    list_filter = ('is_critical',)
    search_fields = ('name', 'label')

@admin.register(SoundType)
class SoundTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'label', 'is_critical', 'created_at')
    list_filter = ('is_critical',)
    search_fields = ('name', 'label')
    ordering = ('name',)