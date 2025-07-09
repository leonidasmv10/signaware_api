"""
Nodos del agente de audio inteligente para Signaware.
Cada nodo representa una etapa del procesamiento de audio.
"""

import os
import logging
import tempfile
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from .state import AgentState

# Configurar logging
logger = logging.getLogger(__name__)


class AudioProcessor:
    """Clase para manejar el procesamiento de audio."""
    
    def __init__(self):
        """Inicializa los componentes de procesamiento de audio."""
        try:
            from .tools.audio_analyzer.yamnet_analyzer import YAMNetAudioAnalyzer
            from .tools.audio_transcription.audio_transcriber import AudioTranscriber
            
            self.analyzer = YAMNetAudioAnalyzer()
            self.transcriber = AudioTranscriber(verbose=False)
            
        except ImportError as e:
            logger.error(f"Error importing audio processing modules: {e}")
            raise


# Instancia global del procesador de audio
audio_processor = AudioProcessor()


def save_uploaded_audio_node(state: AgentState) -> AgentState:
    """
    Nodo para guardar el audio subido desde el frontend.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        AgentState: Estado actualizado con la ruta del audio
    """
    logger.info("Ejecutando nodo: save_uploaded_audio_node")
    
    try:
        # El audio ya viene en el estado desde el frontend
        audio_file = state.get("audio_file")
        
        if not audio_file:
            logger.error("No hay archivo de audio en el estado")
            state["messages"].append(
                SystemMessage(content="ERROR: No se recibió archivo de audio")
            )
            return state
        
        logger.info(f"Archivo recibido: {audio_file.name}")
        logger.info(f"Tamaño del archivo: {audio_file.size} bytes")
        logger.info(f"Content-Type: {audio_file.content_type}")
        
        # Verificar que el archivo no esté vacío
        if audio_file.size == 0:
            logger.error("Archivo de audio vacío")
            state["messages"].append(
                SystemMessage(content="ERROR: El archivo de audio está vacío")
            )
            return state
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            bytes_written = 0
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
                bytes_written += len(chunk)
            temp_path = temp_file.name
        
        logger.info(f"Archivo guardado: {temp_path}")
        logger.info(f"Bytes escritos: {bytes_written}")
        
        # Verificar que el archivo se guardó correctamente
        if not os.path.exists(temp_path):
            logger.error(f"El archivo temporal no se creó: {temp_path}")
            state["messages"].append(
                SystemMessage(content="ERROR: No se pudo crear el archivo temporal")
            )
            return state
        
        file_size = os.path.getsize(temp_path)
        logger.info(f"Tamaño del archivo guardado: {file_size} bytes")
        
        if file_size == 0:
            logger.error("El archivo guardado está vacío")
            state["messages"].append(
                SystemMessage(content="ERROR: El archivo guardado está vacío")
            )
            return state
        
        # Actualizar estado
        state["audio_path"] = temp_path
        
        # Solo agregar mensaje si no existe ya
        audio_saved_msg = f"Audio guardado exitosamente en: {temp_path} ({file_size} bytes)"
        existing_messages = [msg.content for msg in state["messages"]]
        if audio_saved_msg not in existing_messages:
            state["messages"].append(
                HumanMessage(content=audio_saved_msg)
            )
        
        logger.info(f"Audio guardado exitosamente en: {temp_path} ({file_size} bytes)")
        return state
        
    except Exception as e:
        logger.error(f"Error en save_uploaded_audio_node: {e}")
        logger.exception("Traceback completo:")
        state["messages"].append(
            SystemMessage(content=f"ERROR: No se pudo guardar el audio: {str(e)}")
        )
        return state


def audio_analysis_node(state: AgentState) -> AgentState:
    """
    Nodo para analizar el tipo de sonido en el audio.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        AgentState: Estado actualizado con el tipo de sonido detectado
    """
    logger.info("Ejecutando nodo: audio_analysis_node")
    
    try:
        # Verificar que existe la ruta del audio
        if not state.get("audio_path") or not os.path.exists(state["audio_path"]):
            logger.error("No hay ruta de audio válida para analizar")
            state["is_conversation_detected"] = False
            state["sound_type"] = "Unknown"
            state["confidence"] = 0.0
            state["sound_detections"] = []
            state["messages"].append(
                SystemMessage(content="ERROR: No se encontró audio válido para analizar")
            )
            return state
        
        # Analizar el audio con filtro de sonidos relevantes
        try:
            filtered_analysis_result = audio_processor.analyzer.analyze_file_with_filter(state["audio_path"])
            
            # Guardar resultados filtrados
            state["sound_detections"] = filtered_analysis_result if filtered_analysis_result else []
            
            # Extraer el resultado principal (el más probable)
            if filtered_analysis_result:
                sound_type = filtered_analysis_result[0][0] if filtered_analysis_result else "Unknown"
                confidence = filtered_analysis_result[0][1] if filtered_analysis_result and len(filtered_analysis_result[0]) > 1 else 0.0
                alert_category = filtered_analysis_result[0][2] if filtered_analysis_result and len(filtered_analysis_result[0]) > 2 else "unknown"
            else:
                sound_type = "Unknown"
                confidence = 0.0
                alert_category = "unknown"
                
        except Exception as analysis_error:
            logger.error(f"Error en análisis con filtro: {analysis_error}")
            logger.info("Intentando análisis sin filtro...")
            
            # Fallback: análisis sin filtro
            try:
                analysis_result = audio_processor.analyzer.analyze_file(state["audio_path"])
                state["sound_detections"] = analysis_result if analysis_result else []
                
                if analysis_result:
                    sound_type = analysis_result[0][0] if analysis_result else "Unknown"
                    confidence = analysis_result[0][1] if analysis_result and len(analysis_result[0]) > 1 else 0.0
                    alert_category = "unknown"
                else:
                    sound_type = "Unknown"
                    confidence = 0.0
                    alert_category = "unknown"
                    
            except Exception as fallback_error:
                logger.error(f"Error en análisis fallback: {fallback_error}")
                sound_type = "Error"
                confidence = 0.0
                alert_category = "unknown"
                state["sound_detections"] = []
        
        # Actualizar estado
        state["sound_type"] = sound_type
        state["confidence"] = confidence
        state["alert_category"] = alert_category
        state["is_conversation_detected"] = sound_type == "Speech"
        
        # Crear mensaje con resultados filtrados
        if sound_type == "Error":
            detection_summary = "❌ Error en el análisis de audio. Verifica que el archivo sea válido."
        elif state["sound_detections"]:
            detection_summary = "🎯 Sonidos relevantes detectados:\n"
            for i, (detected_sound, detected_confidence, category) in enumerate(state["sound_detections"], 1):
                category_emoji = {
                    'danger_alert': '🔴',
                    'attention_alert': '🟡', 
                    'social_alert': '🟢',
                    'environment_alert': '🔵',
                    'unknown': '❓'
                }.get(category, '❓')
                detection_summary += f"  {i}. {category_emoji} {detected_sound}: {detected_confidence:.3f} ({category})\n"
        else:
            detection_summary = "❌ No se detectaron sonidos relevantes en el audio."
        
        # Solo agregar mensaje si no existe ya
        existing_messages = [msg.content for msg in state["messages"]]
        if detection_summary not in existing_messages:
            state["messages"].append(
                SystemMessage(content=detection_summary)
            )
        
        logger.info(f"Tipo de sonido detectado: {sound_type} (confianza: {confidence:.2f})")
        logger.info(f"Todos los resultados: {state['sound_detections']}")
        return state
        
    except Exception as e:
        logger.error(f"Error en audio_analysis_node: {e}")
        state["is_conversation_detected"] = False
        state["sound_type"] = "Error"
        state["confidence"] = 0.0
        state["sound_detections"] = []
        state["messages"].append(
            SystemMessage(content=f"ERROR en análisis de audio: {str(e)}")
        )
        return state


def audio_transcription_node(state: AgentState) -> AgentState:
    """
    Nodo para transcribir audio cuando se detecta conversación.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        AgentState: Estado actualizado con la transcripción
    """
    logger.info("Ejecutando nodo: audio_transcription_node")
    
    try:
        # Verificar que existe la ruta del audio
        if not state.get("audio_path") or not os.path.exists(state["audio_path"]):
            logger.error("No hay ruta de audio válida para transcribir")
            state["transcription"] = ""
            state["messages"].append(
                SystemMessage(content="ERROR: No se encontró audio válido para transcribir")
            )
            return state
        
        # Transcribir el audio
        transcription_result = audio_processor.transcriber.transcribe_file(state["audio_path"])
        
        # Actualizar estado
        state["transcription"] = transcription_result if transcription_result else ""
        
        state["messages"].append(
            SystemMessage(content=f"Transcripción completada: {state['transcription'][:100]}...")
        )
        
        logger.info(f"Transcripción completada: {len(state['transcription'])} caracteres")
        return state
        
    except Exception as e:
        logger.error(f"Error en audio_transcription_node: {e}")
        state["transcription"] = ""
        state["messages"].append(
            SystemMessage(content=f"ERROR en transcripción: {str(e)}")
        )
        return state


def cleanup_audio_node(state: AgentState) -> AgentState:
    """
    Nodo para limpiar archivos temporales de audio.
    NOTA: No eliminamos el archivo inmediatamente para permitir descarga.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        AgentState: Estado actualizado
    """
    logger.info("Ejecutando nodo: cleanup_audio_node")
    
    try:
        # Por ahora no eliminamos el archivo para permitir descarga
        # En producción, implementar un sistema de limpieza programada
        if state.get("audio_path") and os.path.exists(state["audio_path"]):
            file_size = os.path.getsize(state["audio_path"])
            logger.info(f"Archivo temporal mantenido para descarga: {state['audio_path']} ({file_size} bytes)")
        
        # No limpiamos la referencia para que esté disponible en el endpoint
        # state["audio_path"] = None
        
        return state
        
    except Exception as e:
        logger.error(f"Error en cleanup_audio_node: {e}")
        return state


def show_sound_type_node(state: AgentState) -> AgentState:
    """
    Nodo para mostrar información del tipo de sonido detectado.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        AgentState: Estado sin cambios
    """
    logger.info("Ejecutando nodo: show_sound_type_node")
    
    sound_type = state.get("sound_type", "Unknown")
    confidence = state.get("confidence", 0.0)
    
    # Solo agregar mensaje si no existe ya
    sound_type_msg = f"Tipo de sonido detectado: {sound_type} (confianza: {confidence:.2f})"
    existing_messages = [msg.content for msg in state["messages"]]
    if sound_type_msg not in existing_messages:
        state["messages"].append(
            SystemMessage(content=sound_type_msg)
        )
    
    logger.info(f"Tipo de sonido: {sound_type} (confianza: {confidence:.2f})")
    return state 