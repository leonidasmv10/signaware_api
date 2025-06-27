from django.db import models

# Create your models here.
class SoundType(models.Model):
    type_name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

class VehicleType(models.Model):
    type_name = models.CharField(max_length=50, unique=True)
    description = models.TextField()