from django.contrib import admin
from .models import SoundCategory

@admin.register(SoundCategory)
class SoundCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'label', 'emoji')