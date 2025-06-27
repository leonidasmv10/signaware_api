from django.urls import path
from .views import VehicleTypeCreateView, SoundTypeCreateView

urlpatterns = [
    path('vehicle-type/', VehicleTypeCreateView.as_view(), name='vehicle_type_create'),
    path('sound-type/', SoundTypeCreateView.as_view(), name='sound_type_create'),
]
