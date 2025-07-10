from django.db import models
from django.conf import settings

# Create your models here.

class SoundCategory(models.Model):
    """Categorías de sonidos para clasificación global"""
    name = models.CharField(max_length=100, unique=True)  # Ej: siren, car_horn, etc.
    label = models.CharField(max_length=100)  # Etiqueta para mostrar al usuario
    emoji = models.CharField(max_length=10, blank=True, null=True)  # Emoji para la categoría
    description = models.TextField(blank=True, null=True)
    is_critical = models.BooleanField(default=False)  # Si es una categoría crítica
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label} ({self.name})"

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Sound Categories"

class SoundType(models.Model):
    """Tipos de sonidos que pueden ser detectados (global)"""
    name = models.CharField(max_length=100, unique=True)  # Ej: speech, siren, car_horn, etc.
    label = models.CharField(max_length=100)  # Etiqueta para mostrar al usuario
    description = models.TextField(blank=True, null=True)
    is_critical = models.BooleanField(default=False)  # Si es un sonido crítico que requiere atención
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label} ({self.name})"

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Sound Types"
