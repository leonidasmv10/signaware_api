from ..providers.text_generation.text_generator_manager import text_generator_manager
from ..services.intention_classifier_service import (
    IntentionClassifierService,
)
from ..workflows.chatbot_worklow import ChatbotWorkflow
from .base_agent import BaseAgent


class ChatbotAgent(BaseAgent):
   
    def _setup_components(self):
        """Configura los componentes específicos del agente"""
        # Inicializar generadores de texto a través del manager
        self.text_generator_manager = text_generator_manager
        self.intention_classifier_service = IntentionClassifierService()
        
        # Inicializar workflow
        self.workflow = ChatbotWorkflow()
        
        # Pasar la instancia del clasificador a los nodos
        self.workflow.nodes.intention_classifier = self.intention_classifier_service
        

    def execute(self, user_input: str) -> str:
        """
        Ejecuta el workflow del chatbot con detector de intenciones.
        
        Args:
            user_input: Entrada del usuario
                
        Returns:
            str: Respuesta del chatbot
        """
        try:
            # Obtener estado inicial
            initial_state = self.workflow.get_initial_state()
            
            # Configurar el estado con los datos de entrada
            initial_state["user_input"] = user_input

            # Ejecutar el workflow
            final_state = self.workflow.execute(initial_state)
            
            # Obtener resultado
            response = final_state.get("response", "No se pudo generar una respuesta.")
            # detected_intent = final_state.get("detected_intent", "GENERAL_QUERY")
            
            # # Formatear respuesta
            # result = f"🤖 Chatbot: {response}\n\n📋 Intención detectada: {detected_intent}"
            
            return response
            
        except Exception as e:
            error_msg = f"❌ Error en el chatbot: {e}"
            print(error_msg)
            return "Lo siento, no pude procesar tu consulta. ¿Podrías intentar de nuevo?"
    
    def chat(self, user_input: str) -> dict:
        """
        Método específico para chat.
        
        Args:
            user_input: Entrada del usuario
            
        Returns:
            dict: Respuesta con información detallada
        """
        try:
            # Obtener estado inicial
            initial_state = self.workflow.get_initial_state()
            initial_state["user_input"] = user_input

            # Ejecutar el workflow
            final_state = self.workflow.execute(initial_state)
            
            # Preparar respuesta
            response = {
                "response": final_state.get("response", "No se pudo generar una respuesta."),
                "detected_intent": final_state.get("detected_intent", "GENERAL_QUERY"),
                "conversation_history": final_state.get("conversation_history", []),
                "messages": final_state.get("messages", [])
            }
            
            return response
            
        except Exception as e:
            error_msg = f"❌ Error en el chat: {e}"
            print(error_msg)
            return {
                "response": "Lo siento, no pude procesar tu consulta. ¿Podrías intentar de nuevo?",
                "detected_intent": "GENERAL_QUERY",
                "conversation_history": [],
                "messages": []
            }
    
    def get_conversation_history(self) -> list:
        """
        Obtiene el historial de conversación.
        
        Returns:
            list: Historial de conversación
        """
        try:
            # Obtener estado inicial
            initial_state = self.workflow.get_initial_state()
            return initial_state.get("conversation_history", [])
        except Exception as e:
            print(f"❌ Error obteniendo historial: {e}")
            return []
    
    def clear_conversation_history(self):
        """Limpia el historial de conversación."""
        try:
            # Obtener estado inicial limpio
            initial_state = self.workflow.get_initial_state()
            initial_state["conversation_history"] = []
            initial_state["messages"] = []
            print("✅ Historial de conversación limpiado")
        except Exception as e:
            print(f"❌ Error limpiando historial: {e}")
    
    def get_detailed_status(self) -> dict:
        """
        Obtiene información detallada del estado del agente.
        
        Returns:
            dict: Información detallada del agente
        """
        base_status = self.get_status()
        base_status.update({
            "workflow_initialized": self.workflow.compiled_workflow is not None,
            "components_initialized": {
                "text_generator_manager": self.text_generator_manager is not None,
                "intention_classifier": self.intention_classifier_service.is_initialized if hasattr(self.intention_classifier_service, 'is_initialized') else True
            },
            "chatbot_features": {
                "intent_detection": True,
                "conversation_history": True
            }
        })
        return base_status
