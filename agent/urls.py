"""
URLs del agente de audio inteligente para Signaware.
Define las rutas para los endpoints de procesamiento de audio.
"""

from django.urls import path
from .views import process_audio, health_check, process_audio_legacy, get_audio, GeminiChatView

app_name = 'agent'

urlpatterns = [
    # Endpoint principal para procesamiento de audio (DRF)
    path(
        'process-audio/',
        process_audio,
        name='process_audio'
    ),
    
    # Endpoint para obtener audio procesado
    path(
        'audio/<str:audio_id>/',
        get_audio,
        name='get_audio'
    ),
    
    # Endpoint para verificar el estado del agente
    path(
        'health/',
        health_check,
        name='health_check'
    ),
    
    # Endpoint legacy para compatibilidad
    path(
        'process-audio-legacy/',
        process_audio_legacy,
        name='process_audio_legacy'
    ),
    
    # Endpoint para generación de texto
    path(
        'text_generation/',
        GeminiChatView.as_view(),
        name='text_generation'
    ),
] 