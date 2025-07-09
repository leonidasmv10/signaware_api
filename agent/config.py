"""
Configuración del agente de audio inteligente para Signaware.
Define configuraciones, constantes y parámetros del sistema.
"""

import os
from typing import List

# Configuración de logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Configuración de audio
AUDIO_CONFIG = {
    'duration': 3,  # Duración de grabación en segundos
    'sample_rate': 16000,  # Tasa de muestreo
    'channels': 1,  # Mono
    'format': 'wav',  # Formato de audio
    'verbose': False  # Modo verbose para debugging
}

# Tipos de archivo de audio permitidos
ALLOWED_AUDIO_TYPES = [
    'audio/wav',
    'audio/mp3', 
    'audio/mpeg',
    'audio/ogg',
    'audio/flac'
]

# Configuración de confianza
CONFIDENCE_THRESHOLDS = {
    'speech_detection': 0.5,  # Umbral mínimo para detectar conversación
    'high_confidence': 0.8,   # Confianza alta
    'medium_confidence': 0.6,  # Confianza media
    'low_confidence': 0.3     # Confianza baja
}

# Tipos de sonido que se pueden detectar
SOUND_TYPES = [
    'Speech',
    'Music',
    'Noise',
    'Silence',
    'Vehicle',
    'Siren',
    'Horn',
    'Unknown'
]

# Configuración de rutas
PATHS = {
    'audio_fragments': 'audio_fragments',
    'models': 'models',
    'temp': 'temp'
}

# Configuración del workflow
WORKFLOW_CONFIG = {
    'max_execution_time': 30,  # Tiempo máximo de ejecución en segundos
    'retry_attempts': 3,       # Número de intentos de reintento
    'cleanup_temp_files': True # Limpiar archivos temporales
}

# Mensajes del sistema
SYSTEM_MESSAGES = {
    'startup': 'Iniciando el sistema de monitoreo de audio de Signaware.',
    'processing': 'Procesando audio...',
    'success': 'Procesamiento completado exitosamente.',
    'error': 'Error en el procesamiento de audio.',
    'no_audio': 'No se encontró audio para procesar.',
    'invalid_format': 'Formato de audio no soportado.',
    'workflow_unavailable': 'Sistema de procesamiento no disponible.'
}

# Configuración de respuesta
RESPONSE_CONFIG = {
    'include_messages': True,      # Incluir mensajes del sistema en la respuesta
    'include_confidence': True,    # Incluir nivel de confianza
    'include_audio_path': False,   # Incluir ruta del archivo de audio
    'max_transcription_length': 1000  # Longitud máxima de transcripción
}

def get_audio_folder() -> str:
    """Obtiene la ruta de la carpeta de audio."""
    return os.path.join(os.getcwd(), PATHS['audio_fragments'])

def get_models_folder() -> str:
    """Obtiene la ruta de la carpeta de modelos."""
    return os.path.join(os.getcwd(), PATHS['models'])

def get_temp_folder() -> str:
    """Obtiene la ruta de la carpeta temporal."""
    return os.path.join(os.getcwd(), PATHS['temp'])

def create_directories():
    """Crea las carpetas necesarias si no existen."""
    directories = [
        get_audio_folder(),
        get_models_folder(),
        get_temp_folder()
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True) 

# Diccionario de sonidos relevantes para filtrar
RELEVANT_SOUNDS_DICT = {
    'Alarm': 'danger_alert',
    'Fire alarm': 'danger_alert',
    'Smoke detector': 'danger_alert',
    'Siren': 'danger_alert',
    'Civil defense siren': 'danger_alert',
    'Telephone bell ringing': 'attention_alert',
    'Ringtone': 'attention_alert',
    'Doorbell': 'attention_alert',
    'Ding-dong': 'attention_alert',
    'Whistle': 'attention_alert',
    'Shout': 'social_alert',
    'Yell': 'social_alert',
    'Children shouting': 'social_alert',
    'Screaming': 'social_alert',
    'Speech': 'social_alert',
    'Child speech': 'social_alert',
    'Conversation': 'social_alert',
    'Crying': 'social_alert',
    'Baby cry': 'social_alert',
    'Laughter': 'social_alert',
    'Baby laughter': 'social_alert',
    'Giggle': 'social_alert',
    'Run': 'environment_alert',
    'Footsteps': 'environment_alert',
    'Vehicle horn': 'danger_alert',
    'Car alarm': 'danger_alert',
    'Reversing beeps': 'danger_alert',
    'Train': 'environment_alert',
    'Subway': 'environment_alert',
    'Car passing by': 'environment_alert',
    'Dog': 'environment_alert',
    'Bark': 'environment_alert',
    'Whimper (dog)': 'social_alert',
    'Glass': 'danger_alert',
    'Shatter': 'danger_alert',
    'Door': 'environment_alert',
    'Slam': 'attention_alert',
    'Knock': 'attention_alert',
    'Toilet flush': 'environment_alert',
    'Frying (food)': 'environment_alert',
    'Water tap': 'environment_alert',
    'Fire': 'danger_alert',
    'Crackle': 'danger_alert',
    'Children playing': 'social_alert',
    'Applause': 'social_alert',
    'Crowd': 'social_alert',
    'Thunder': 'environment_alert',
    'Rain': 'environment_alert',
    'Rain on surface': 'environment_alert',
}

# Configuración del filtro de sonidos
SOUND_FILTER_CONFIG = {
    'enabled': True,  # Habilitar filtro de sonidos relevantes
    'min_confidence': 0.3,  # Confianza mínima para considerar un sonido relevante
    'include_unknown': False,  # Incluir sonidos no clasificados
    'alert_categories': {
        'danger_alert': '🔴 Peligro',
        'attention_alert': '🟡 Atención', 
        'social_alert': '🟢 Social',
        'environment_alert': '�� Entorno'
    }
} 