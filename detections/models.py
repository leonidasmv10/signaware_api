from django.db import models
from django.contrib.auth.models import User
from core.models import VehicleType, SoundType

STATUS_CHOICES = [
    ("normal", "Normal"),
    ("warning", "Warning"),
    ("critical", "Critical"),
]


class VisualDetection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    frequency = models.IntegerField(default=0)
    detection_date = models.DateTimeField(auto_now_add=True)


class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitud = models.FloatField()
    longitud = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)


class AudioDetection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sound_type = models.ForeignKey(SoundType, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    detection_date = models.DateTimeField(auto_now_add=True)
