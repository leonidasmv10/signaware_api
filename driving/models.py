from django.db import models
from django.contrib.auth.models import User

class DrivingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_horns = models.IntegerField()
    total_sirens = models.IntegerField()
    registration_date = models.DateTimeField(auto_now_add=True)
