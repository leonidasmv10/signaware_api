from rest_framework import generics, permissions
from .models import DrivingHistory
from .serializers import DrivingHistorySerializer

class DrivingHistoryListCreateView(generics.ListCreateAPIView):
    queryset = DrivingHistory.objects.all()
    serializer_class = DrivingHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
