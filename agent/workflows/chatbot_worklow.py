"""
Workflow del agente de audio inteligente para Signaware.
Define el grafo de flujo de trabajo usando LangGraph.
"""

import logging
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from ..nodes.chatbot_nodes import ChatbotNodes
from ..states.chatbot_state import ChatbotState

# Configurar logging
logger = logging.getLogger(__name__)


class ChatbotWorkflow:

    def __init__(self):
        """Inicializa el workflow y sus componentes."""
        self.logger = logging.getLogger(__name__)
        self.nodes = ChatbotNodes()
        self.workflow_graph = None
        self.compiled_workflow = None
        self._create_workflow()
    
    def _create_workflow(self):
        """Crea y configura el grafo de flujo de trabajo del agente."""
        self.logger.info("Creando workflow del agente")
        
        # Crear el grafo
        self.workflow_graph = StateGraph(ChatbotState)
        
        # Añadir nodos
        self.workflow_graph.add_node("save_uploaded_audio_node", self.nodes.save_uploaded_audio_node)
        self.workflow_graph.add_node("audio_analysis_node", self.nodes.audio_analysis_node)
        self.workflow_graph.add_node("audio_transcription_node", self.nodes.audio_transcription_node)
        self.workflow_graph.add_node("show_sound_type_node", self.nodes.show_sound_type_node)
        self.workflow_graph.add_node("cleanup_audio_node", self.nodes.cleanup_audio_node)
        
        # Definir los bordes
        # 1. El flujo comienza con guardar el audio subido
        self.workflow_graph.add_edge(START, "save_uploaded_audio_node")
        
        # 2. Después de guardar, el audio se analiza
        self.workflow_graph.add_edge("save_uploaded_audio_node", "audio_analysis_node")
        
        # 3. Borde condicional desde 'audio_analysis_node'
        self.workflow_graph.add_conditional_edges(
            "audio_analysis_node",
            self._decide_what_to_do_with_audio,
            {
                "audio_transcription_node": "audio_transcription_node",
                "show_sound_type_node": "show_sound_type_node"
            }
        )
        
        # 4. Después de procesar, limpiar archivos temporales
        self.workflow_graph.add_edge("audio_transcription_node", "cleanup_audio_node")
        self.workflow_graph.add_edge("show_sound_type_node", "cleanup_audio_node")
        
        # 5. El nodo de limpieza termina el flujo
        self.workflow_graph.add_edge("cleanup_audio_node", END)
        
        # Compilar el workflow
        try:
            self.compiled_workflow = self.workflow_graph.compile()
            self.logger.info("Workflow creado y compilado exitosamente")
        except Exception as e:
            self.logger.error(f"Error compilando workflow: {e}")
            self.compiled_workflow = None
    
    
    def get_initial_state(self) -> ChatbotState:
        """
        Crea el estado inicial del agente.
        
        Returns:
            ChatbotState: Estado inicial configurado
        """
        return {
            "messages": [],  # Iniciar con mensajes vacíos para evitar duplicación
            "is_conversation_detected": False,
            "audio_file": None,
            "audio_path": "",
            "sound_type": "",
            "transcription": "",
            "confidence": 0.0
        }
    
    def execute(self, initial_state: ChatbotState) -> ChatbotState:
        """
        Ejecuta el workflow con el estado inicial proporcionado.
        
        Args:
            initial_state: Estado inicial para la ejecución
            
        Returns:
            ChatbotState: Estado final después de la ejecución
        """
        if not self.compiled_workflow:
            raise RuntimeError("Workflow no está compilado correctamente")
        
        try:
            final_state = self.compiled_workflow.invoke(initial_state)
            return final_state
        except Exception as e:
            self.logger.error(f"Error ejecutando workflow: {e}")
            raise
