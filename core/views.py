from rest_framework import generics
from .models import VehicleType, SoundType
from .serializers import VehicleTypeSerializer, SoundTypeSerializer
from rest_framework.permissions import IsAdminUser

class VehicleTypeCreateView(generics.CreateAPIView):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [IsAdminUser]

class SoundTypeCreateView(generics.CreateAPIView):
    queryset = SoundType.objects.all()
    serializer_class = SoundTypeSerializer
    permission_classes = [IsAdminUser]