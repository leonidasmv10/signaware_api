from django.db import models
from django.contrib.auth.models import User

ALERT_TYPE_CHOICES = [('visual', 'Visual'), ('audio', 'Audio'), ('vibration', 'Vibration')]
VEHICLE_TYPE_CHOICES = [('car', 'Car'), ('motorcycle', 'Motorcycle'), ('bicycle', 'Bicycle'), ('truck', 'Truck')]
SUSCRIPTION_CHOICES = [('free', 'Free'), ('', 'None')]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    preferred_alert_type = models.CharField(max_length=10, choices=ALERT_TYPE_CHOICES, default='visual')
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES, default='car')
    suscription = models.CharField(max_length=10, choices=SUSCRIPTION_CHOICES, default='free')
