"""
Workflow del agente de chatbot inteligente para Signaware.
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
        """Crea y configura el grafo de flujo de trabajo del chatbot."""
        self.logger.info("Creando workflow del chatbot con nodos específicos por intención")
        
        # Crear el grafo
        self.workflow_graph = StateGraph(ChatbotState)
        
        # Añadir nodo de clasificación de intención
        self.workflow_graph.add_node("classify_intent_node", self.nodes.classify_intent_node)
        
        # Añadir nodos específicos por categoría de intención
        self.workflow_graph.add_node("hearing_aids_node", self.nodes.hearing_aids_node)
        self.workflow_graph.add_node("visual_signals_node", self.nodes.visual_signals_node)
        self.workflow_graph.add_node("audio_translation_node", self.nodes.audio_translation_node)
        self.workflow_graph.add_node("medical_center_node", self.nodes.medical_center_node)
        self.workflow_graph.add_node("recommend_app_node", self.nodes.recommend_app_node)
        self.workflow_graph.add_node("know_rights_node", self.nodes.know_rights_node)
        self.workflow_graph.add_node("certificate_node", self.nodes.certificate_node)
        self.workflow_graph.add_node("sound_report_node", self.nodes.sound_report_node)
        self.workflow_graph.add_node("general_query_node", self.nodes.general_query_node)
        
        # Definir los bordes del chatbot
        # 1. El flujo comienza con clasificación de intención
        self.workflow_graph.add_edge(START, "classify_intent_node")
        
        # 2. Borde condicional desde 'classify_intent_node' hacia nodos específicos
        self.workflow_graph.add_conditional_edges(
            "classify_intent_node",
            self._route_to_specific_node,
            {
                "hearing_aids_node": "hearing_aids_node",
                "visual_signals_node": "visual_signals_node",
                "audio_translation_node": "audio_translation_node",
                "medical_center_node": "medical_center_node",
                "recommend_app_node": "recommend_app_node",
                "know_rights_node": "know_rights_node",
                "certificate_node": "certificate_node",
                "sound_report_node": "sound_report_node",
                "general_query_node": "general_query_node"
            }
        )
        
        # 3. Todos los nodos específicos terminan el flujo
        self.workflow_graph.add_edge("hearing_aids_node", END)
        self.workflow_graph.add_edge("visual_signals_node", END)
        self.workflow_graph.add_edge("audio_translation_node", END)
        self.workflow_graph.add_edge("medical_center_node", END)
        self.workflow_graph.add_edge("recommend_app_node", END)
        self.workflow_graph.add_edge("know_rights_node", END)
        self.workflow_graph.add_edge("certificate_node", END)
        self.workflow_graph.add_edge("sound_report_node", END)
        self.workflow_graph.add_edge("general_query_node", END)
        
        # Compilar el workflow
        try:
            self.compiled_workflow = self.workflow_graph.compile()
            self.logger.info("Workflow del chatbot con nodos específicos creado y compilado exitosamente")
        except Exception as e:
            self.logger.error(f"Error compilando workflow: {e}")
            self.compiled_workflow = None
    
    def _route_to_specific_node(self, state: dict) -> str:
        """
        Rutea hacia el nodo específico según la intención detectada.
        
        Args:
            state: Estado actual con la intención detectada
            
        Returns:
            str: Nombre del nodo específico a ejecutar
        """
        detected_intent = state.get("detected_intent", "GENERAL_QUERY")
        
        # Mapeo de intenciones a nodos
        intent_to_node = {
            "HEARING_AIDS": "hearing_aids_node",
            "VISUAL_SIGNALS": "visual_signals_node",
            "AUDIO_TRANSLATION": "audio_translation_node",
            "MEDICAL_CENTER": "medical_center_node",
            "RECOMMEND_APP": "recommend_app_node",
            "KNOW_RIGHTS": "know_rights_node",
            "CERTIFICATE": "certificate_node",
            "SOUND_REPORT": "sound_report_node",
            "GENERAL_QUERY": "general_query_node"
        }
        
        # Obtener el nodo correspondiente o usar general_query_node como fallback
        target_node = intent_to_node.get(detected_intent, "general_query_node")
        
        self.logger.info(f"Ruteando intención '{detected_intent}' hacia nodo '{target_node}'")
        
        return target_node
    
    def get_initial_state(self) -> ChatbotState:
        """
        Crea el estado inicial del chatbot.
        
        Returns:
            ChatbotState: Estado inicial configurado
        """
        return {
            "messages": [],
            "user_input": "",
            "detected_intent": "",
            "response": "",
            "conversation_history": []
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
