from django.urls import path
from .views import DrivingHistoryListCreateView

urlpatterns = [
    path('history/', DrivingHistoryListCreateView.as_view(), name='driving_history'),
]
