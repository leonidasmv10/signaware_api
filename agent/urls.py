from django.urls import path, include
from .views import (
    process_audio,
    get_audio,
    health_check,
    process_audio_legacy,
    AgentView,
)
from rest_framework.routers import DefaultRouter
from .views import DetectedSoundViewSet

router = DefaultRouter()
router.register(r'detected-sounds', DetectedSoundViewSet)

urlpatterns = [
    # Endpoints personalizados
    path("process-audio/", process_audio, name="process_audio"),
    path("audio/<str:audio_id>/", get_audio, name="get_audio"),
    path("health/", health_check, name="health_check"),
    path("process-audio-legacy/", process_audio_legacy, name="process_audio_legacy"),
    path("text_generation/", AgentView.as_view(), name="text_generation"),
    # Endpoints REST automáticos
    *router.urls,
]