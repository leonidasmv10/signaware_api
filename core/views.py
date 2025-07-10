from rest_framework import viewsets
from .models import SoundCategory
from .serializers import SoundCategorySerializer

class SoundCategoryViewSet(viewsets.ModelViewSet):
    queryset = SoundCategory.objects.all()
    serializer_class = SoundCategorySerializer

