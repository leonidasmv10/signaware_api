from django.urls import path
from .views import (
    VisualDetectionCreateView,
    LocationCreateView,
    AudioDetectionCreateView,
    AudioDetectionListView,
    DailySummaryView,
)

urlpatterns = [
    path(
        "visual/create/",
        VisualDetectionCreateView.as_view(),
        name="create_visual_detection",
    ),
    path("location/create/", LocationCreateView.as_view(), name="create_location"),
    path(
        "audio/create/",
        AudioDetectionCreateView.as_view(),
        name="create_audio_detection",
    ),
    path("audio_list/", AudioDetectionListView.as_view(), name="list_audio_detections"),
    path("daily_summary/", DailySummaryView.as_view(), name="daily_summary"),
]
