"""
Workflow del agente de audio inteligente para Signaware.
Define el grafo de flujo de trabajo usando LangGraph.
"""

import logging
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .nodes import (
    save_uploaded_audio_node,
    audio_analysis_node,
    audio_transcription_node,
    show_sound_type_node,
    cleanup_audio_node
)

# Configurar logging
logger = logging.getLogger(__name__)


def decide_what_to_do_with_audio(state: AgentState) -> str:
    """
    Función de decisión para el borde condicional.
    Decide si el flujo debe ir al nodo de transcripción o mostrar el tipo de sonido.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        str: Nombre del siguiente nodo a ejecutar
    """
    logger.info("Ejecutando función de decisión")
    
    sound_type = state.get("sound_type", "Unknown")
    confidence = state.get("confidence", 0.0)
    
    logger.info(f"Decisión basada en: {sound_type} (confianza: {confidence:.2f})")
    
    # Si es conversación y tiene buena confianza, transcribir
    if sound_type == "Speech" and confidence > 0.5:
        logger.info("Decisión: Transcribir audio (conversación detectada)")
        return "audio_transcription_node"
    else:
        logger.info("Decisión: Mostrar tipo de sonido (no es conversación)")
        return "show_sound_type_node"


def create_workflow() -> StateGraph:
    """
    Crea y configura el grafo de flujo de trabajo del agente.
    
    Returns:
        StateGraph: Grafo configurado del agente
    """
    logger.info("Creando workflow del agente")
    
    # Crear el grafo
    workflow = StateGraph(AgentState)
    
    # Añadir nodos
    workflow.add_node("save_uploaded_audio_node", save_uploaded_audio_node)
    workflow.add_node("audio_analysis_node", audio_analysis_node)
    workflow.add_node("audio_transcription_node", audio_transcription_node)
    workflow.add_node("show_sound_type_node", show_sound_type_node)
    workflow.add_node("cleanup_audio_node", cleanup_audio_node)
    
    # Definir los bordes
    # 1. El flujo comienza con guardar el audio subido
    workflow.add_edge(START, "save_uploaded_audio_node")
    
    # 2. Después de guardar, el audio se analiza
    workflow.add_edge("save_uploaded_audio_node", "audio_analysis_node")
    
    # 3. Borde condicional desde 'audio_analysis_node'
    workflow.add_conditional_edges(
        "audio_analysis_node",
        decide_what_to_do_with_audio,
        {
            "audio_transcription_node": "audio_transcription_node",
            "show_sound_type_node": "show_sound_type_node"
        }
    )
    
    # 4. Después de procesar, limpiar archivos temporales
    workflow.add_edge("audio_transcription_node", "cleanup_audio_node")
    workflow.add_edge("show_sound_type_node", "cleanup_audio_node")
    
    # 5. El nodo de limpieza termina el flujo
    workflow.add_edge("cleanup_audio_node", END)
    
    logger.info("Workflow creado exitosamente")
    return workflow


def get_initial_state() -> AgentState:
    """
    Crea el estado inicial del agente.
    
    Returns:
        AgentState: Estado inicial configurado
    """
    return {
        "messages": [HumanMessage(content="Iniciando el sistema de monitoreo de audio de Signaware.")],
        "is_conversation_detected": False,
        "audio_file": None,
        "audio_path": "",
        "sound_type": "",
        "transcription": "",
        "confidence": 0.0
    }


# Crear instancia global del workflow compilado
try:
    workflow_graph = create_workflow()
    compiled_workflow = workflow_graph.compile()
    logger.info("Workflow compilado exitosamente")
except Exception as e:
    logger.error(f"Error compilando workflow: {e}")
    compiled_workflow = None 