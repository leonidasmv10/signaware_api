from django.db import models
from django.conf import settings

# Categoría de sonido relevante
class SoundCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Ej: danger_alert
    label = models.CharField(max_length=100)            # Ej: Alerta de peligro
    emoji = models.CharField(max_length=10, blank=True) # Ej: 🔴

    def __str__(self):
        return f"{self.emoji} {self.label}" if self.emoji else self.label

# Modelos existentes
