"""
Estado del agente de audio inteligente para Signaware.
Define la estructura de datos que se pasa entre los nodos del grafo.
"""

from typing import TypedDict, Annotated, List, Optional
import operator
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    Representa el estado actual del asistente de audio inteligente.
    
    Attributes:
        messages: Lista de mensajes del sistema (se combinan con operator.add)
        is_conversation_detected: Indica si se detectó una conversación
        audio_file: Archivo de audio subido desde el frontend
        audio_path: Ruta del archivo de audio procesado
        sound_type: Tipo de sonido detectado (Speech, Music, etc.)
        transcription: Transcripción del audio (si es conversación)
        confidence: Nivel de confianza de la detección
        alert_category: Categoría de alerta del sonido detectado (danger_alert, attention_alert, etc.)
        sound_detections: Lista de detecciones de sonidos con sus categorías
    """
    messages: Annotated[List[BaseMessage], operator.add]
    is_conversation_detected: bool
    audio_file: Optional[object]  # Django UploadedFile object
    audio_path: str
    sound_type: str
    transcription: str
    confidence: float
    alert_category: str
    sound_detections: List 