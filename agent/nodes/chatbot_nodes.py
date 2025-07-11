"""
Nodos del agente de chatbot inteligente para Signaware.
Cada nodo representa una etapa del procesamiento de conversación.
"""

import os
import logging
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Configurar logging
logger = logging.getLogger(__name__)


class ChatbotNodes:

    def __init__(self):
        """Inicializa los nodos y sus dependencias."""
        self.logger = logging.getLogger(__name__)

    def classify_intent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Nodo para clasificar la intención del usuario.
        
        Args:
            state: Estado actual del chatbot
            
        Returns:
            Dict con la intención detectada
        """
        try:
            user_input = state.get("user_input", "")
            if not user_input:
                state["detected_intent"] = "GENERAL_QUERY"
                return state
            
            # Usar la instancia compartida del clasificador
            if hasattr(self, 'intention_classifier'):
                classifier = self.intention_classifier
            else:
                # Fallback: crear nueva instancia si no está disponible
                from ..services.intention_classifier_service import IntentionClassifierService
                classifier = IntentionClassifierService()
            
            detected_intent = classifier.execute(user_input)
            
            state["detected_intent"] = detected_intent
            self.logger.info(f"Intención detectada: {detected_intent}")
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error en classify_intent_node: {e}")
            state["detected_intent"] = "GENERAL_QUERY"
            return state

    # Nodos específicos por categoría de intención

    def hearing_aids_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo especializado para consultas sobre audífonos"""
        try:
            from ..providers.text_generation.text_generator_manager import text_generator_manager
            
            user_input = state.get("user_input", "")
            
            prompt = f"""
            Eres un amigable especialista en audífonos que ayuda a personas con discapacidad auditiva.
            
            El usuario pregunta: "{user_input}"
            
            Responde de manera:
            - 🎉 Alegre y motivadora
            - 📝 Breve y fácil de entender
            - 💝 Amigable y empática
            - ✨ Con emojis para hacerlo más ameno
            
            Da información práctica sobre:
            - Tipos básicos de audífonos
            - Dónde conseguir ayuda
            - Un consejo útil
            
            Máximo 3-4 líneas. ¡Sé positivo y alentador!
            """
            
            response = text_generator_manager.execute_generator("gemini", prompt)
            state["response"] = response
            self._update_conversation_history(state, "HEARING_AIDS")
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error en hearing_aids_node: {e}")
            state["response"] = "¡Ups! 😅 No pude procesar tu consulta. ¿Me lo preguntas de otra forma? 💪"
            return state

    def visual_signals_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo especializado para señales visuales y alertas"""
        try:
            from ..providers.text_generation.text_generator_manager import text_generator_manager
            
            user_input = state.get("user_input", "")
            
            prompt = f"""
            Eres un amigable especialista en alertas visuales para personas con discapacidad auditiva.
            
            El usuario pregunta: "{user_input}"
            
            Responde de manera:
            - 🎉 Alegre y motivadora
            - 📝 Breve y fácil de entender
            - 💝 Amigable y empática
            - ✨ Con emojis para hacerlo más ameno
            
            Da información práctica sobre:
            - Tipos de alertas visuales
            - Una app o dispositivo útil
            - Un consejo para el hogar
            
            Máximo 3-4 líneas. ¡Sé positivo y alentador!
            """
            
            response = text_generator_manager.execute_generator("gemini", prompt)
            state["response"] = response
            self._update_conversation_history(state, "VISUAL_SIGNALS")
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error en visual_signals_node: {e}")
            state["response"] = "¡Ups! 😅 No pude procesar tu consulta. ¿Me lo preguntas de otra forma? 💪"
            return state

    def audio_translation_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo especializado para transcripción y traducción de audio"""
        try:
            from ..providers.text_generation.text_generator_manager import text_generator_manager
            
            user_input = state.get("user_input", "")
            
            prompt = f"""
            Eres un amigable especialista en transcripción para personas con discapacidad auditiva.
            
            El usuario pregunta: "{user_input}"
            
            Responde de manera:
            - 🎉 Alegre y motivadora
            - 📝 Breve y fácil de entender
            - 💝 Amigable y empática
            - ✨ Con emojis para hacerlo más ameno
            
            Da información práctica sobre:
            - Una app de transcripción útil
            - Cómo funciona básicamente
            - Un consejo para usarla
            
            Máximo 3-4 líneas. ¡Sé positivo y alentador!
            """
            
            response = text_generator_manager.execute_generator("gemini", prompt)
            state["response"] = response
            self._update_conversation_history(state, "AUDIO_TRANSLATION")
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error en audio_translation_node: {e}")
            state["response"] = "¡Ups! 😅 No pude procesar tu consulta. ¿Me lo preguntas de otra forma? 💪"
            return state

    def medical_center_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo especializado para centros médicos y especialistas"""
        try:
            from ..providers.text_generation.text_generator_manager import text_generator_manager
            
            user_input = state.get("user_input", "")
            
            prompt = f"""
            Eres un amigable especialista en salud auditiva que ayuda a personas con discapacidad auditiva.
            
            El usuario pregunta: "{user_input}"
            
            Responde de manera:
            - 🎉 Alegre y motivadora
            - 📝 Breve y fácil de entender
            - 💝 Amigable y empática
            - ✨ Con emojis para hacerlo más ameno
            
            Da información práctica sobre:
            - Dónde encontrar ayuda médica
            - Qué tipo de especialista buscar
            - Un consejo para la consulta
            
            Máximo 3-4 líneas. ¡Sé positivo y alentador!
            """
            
            response = text_generator_manager.execute_generator("gemini", prompt)
            state["response"] = response
            self._update_conversation_history(state, "MEDICAL_CENTER")
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error en medical_center_node: {e}")
            state["response"] = "¡Ups! 😅 No pude procesar tu consulta. ¿Me lo preguntas de otra forma? 💪"
            return state

    def recommend_app_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo especializado para recomendaciones de aplicaciones"""
        try:
            from ..providers.text_generation.text_generator_manager import text_generator_manager
            
            user_input = state.get("user_input", "")
            
            prompt = f"""
            Eres un amigable especialista en apps que ayuda a personas con discapacidad auditiva.
            
            El usuario pregunta: "{user_input}"
            
            Responde de manera:
            - 🎉 Alegre y motivadora
            - 📝 Breve y fácil de entender
            - 💝 Amigable y empática
            - ✨ Con emojis para hacerlo más ameno
            
            Da información práctica sobre:
            - Una app útil para su necesidad
            - Qué hace la app
            - Un consejo para usarla
            
            Máximo 3-4 líneas. ¡Sé positivo y alentador!
            """
            
            response = text_generator_manager.execute_generator("gemini", prompt)
            state["response"] = response
            self._update_conversation_history(state, "RECOMMEND_APP")
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error en recommend_app_node: {e}")
            state["response"] = "¡Ups! 😅 No pude procesar tu consulta. ¿Me lo preguntas de otra forma? 💪"
            return state

    def know_rights_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo especializado para derechos legales y accesibilidad"""
        try:
            from ..providers.text_generation.text_generator_manager import text_generator_manager
            
            user_input = state.get("user_input", "")
            
            prompt = f"""
            Eres un amigable especialista en derechos que empodera a personas con discapacidad auditiva.
            
            El usuario pregunta: "{user_input}"
            
            Responde de manera:
            - 🎉 Alegre y motivadora
            - 📝 Breve y fácil de entender
            - 💝 Amigable y empática
            - ✨ Con emojis para hacerlo más ameno
            
            Da información práctica sobre:
            - Un derecho importante que tienen
            - Dónde pueden pedir ayuda
            - Un consejo para defenderse
            
            Máximo 3-4 líneas. ¡Sé positivo y alentador!
            """
            
            response = text_generator_manager.execute_generator("gemini", prompt)
            state["response"] = response
            self._update_conversation_history(state, "KNOW_RIGHTS")
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error en know_rights_node: {e}")
            state["response"] = "¡Ups! 😅 No pude procesar tu consulta. ¿Me lo preguntas de otra forma? 💪"
            return state

    def certificate_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo especializado para certificados de discapacidad"""
        try:
            from ..providers.text_generation.text_generator_manager import text_generator_manager
            
            user_input = state.get("user_input", "")
            
            prompt = f"""
            Eres un amigable especialista en certificados que ayuda a personas con discapacidad auditiva.
            
            El usuario pregunta: "{user_input}"
            
            Responde de manera:
            - 🎉 Alegre y motivadora
            - 📝 Breve y fácil de entender
            - 💝 Amigable y empática
            - ✨ Con emojis para hacerlo más ameno
            
            Da información práctica sobre:
            - Qué es el certificado
            - Dónde pueden tramitarlo
            - Un consejo para el proceso
            
            Máximo 3-4 líneas. ¡Sé positivo y alentador!
            """
            
            response = text_generator_manager.execute_generator("gemini", prompt)
            state["response"] = response
            self._update_conversation_history(state, "CERTIFICATE")
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error en certificate_node: {e}")
            state["response"] = "¡Ups! 😅 No pude procesar tu consulta. ¿Me lo preguntas de otra forma? 💪"
            return state

    def sound_report_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo especializado para reportes y análisis de sonidos"""
        try:
            from ..providers.text_generation.text_generator_manager import text_generator_manager
            from ..services.sound_report_service import SoundReportService
            
            user_input = state.get("user_input", "")
            
            # Generar reporte de sonidos detectados
            sound_report_service = SoundReportService()
            
            # Extraer parámetros del usuario (si los especifica)
            days = 30  # Por defecto 30 días
            user_id = None  # Por defecto todos los usuarios
            
            # Buscar parámetros en el input del usuario
            if "últimos" in user_input.lower() or "last" in user_input.lower():
                # Extraer número de días si se especifica
                import re
                days_match = re.search(r'(\d+)\s*días?', user_input.lower())
                if days_match:
                    days = int(days_match.group(1))
            
            # Generar reporte
            report = sound_report_service.generate_sound_report(user_id=user_id, days=days)
            
            if "error" in report:
                # Si hay error, generar respuesta amigable
                prompt = f"""
                Eres un amigable especialista en sonidos que ayuda a personas con discapacidad auditiva.
                
                El usuario pregunta: "{user_input}"
                
                Hubo un pequeño problema técnico, pero puedes ayudarle con información básica.
                
                Responde de manera:
                - 🎉 Alegre y motivadora
                - 📝 Breve y fácil de entender
                - 💝 Amigable y empática
                - ✨ Con emojis para hacerlo más ameno
                
                Da información práctica sobre:
                - Una herramienta útil para detectar sonidos
                - Un consejo para estar más seguro
                
                Máximo 3-4 líneas. ¡Sé positivo y alentador!
                """
                
                response = text_generator_manager.execute_generator("gemini", prompt)
                state["response"] = response
                self._update_conversation_history(state, "SOUND_REPORT")
                
                return state
            
            # Generar prompt con datos del reporte
            prompt = self._generate_sound_report_prompt(user_input, report)
            
            response = text_generator_manager.execute_generator("gemini", prompt)
            state["response"] = response
            self._update_conversation_history(state, "SOUND_REPORT")
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error en sound_report_node: {e}")
            state["response"] = "¡Ups! 😅 No pude procesar tu consulta. ¿Me lo preguntas de otra forma? 💪"
            return state

    def _generate_sound_report_prompt(self, user_input: str, report: Dict[str, Any]) -> str:
        """Genera un prompt específico para el reporte de sonidos"""
        
        # Preparar datos del reporte
        summary = report.get("summary", {})
        sound_stats = report.get("sound_type_statistics", [])
        critical_sounds = report.get("critical_sounds", [])
        recommendations = report.get("recommendations", [])
        period = report.get("period", {})
        
        # Datos principales
        total_detections = summary.get('total_detections', 0)
        days = period.get('days', 30)
        
        # Top 5 sonidos más frecuentes
        top_sounds = ""
        if sound_stats:
            top_sounds = "**🎯 Top 5 Sonidos Detectados:**\n"
            for i, stat in enumerate(sound_stats[:5], 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "4️⃣" if i == 4 else "5️⃣"
                top_sounds += f"{emoji} **{stat['label']}**: `{stat['count']} veces`\n"
        
        # Sonido crítico reciente
        critical_info = ""
        if critical_sounds:
            critical_info = f"**🚨 Última Alerta Crítica:** `{critical_sounds[0]['sound_type']}`"
        
        # Recomendación principal
        main_recommendation = ""
        if recommendations:
            main_recommendation = f"**💡 Recomendación Estrella:** > {recommendations[0]}"
        
        prompt = f"""
        Eres un amigable especialista en sonidos que ayuda a personas con discapacidad auditiva.
        
        El usuario pregunta: "{user_input}"
        
        Responde de manera:
        - 🎉 Alegre y motivadora
        - 📝 Breve y directa (máximo 3 líneas)
        - 💝 Amigable y empática
        - ✨ Con emojis y markdown para hacerlo más atractivo
        
        Usa markdown para darle vida:
        - **Texto en negrita** para títulos importantes
        - `Código` para números o datos clave
        - > Citas para destacar información
        - Listas con • o - para organizar datos
        
        Datos del reporte:
        - **📊 Total:** `{total_detections} detecciones` en `{days} días`
        {top_sounds}
        - {critical_info}
        - {main_recommendation}
        
        Da información práctica sobre:
        - Un dato importante del reporte
        - Una recomendación útil
        - Un mensaje de apoyo
        
        ¡Sé positivo y alentador! 💪
        """
        
        return prompt

    def general_query_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo para consultas generales"""
        try:
            from ..providers.text_generation.text_generator_manager import text_generator_manager
            
            user_input = state.get("user_input", "")
            
            prompt = f"""
            Eres un amigable asistente que ayuda a personas con discapacidad auditiva.
            
            El usuario pregunta: "{user_input}"
            
            Responde de manera:
            - 🎉 Alegre y motivadora
            - 📝 Breve y fácil de entender
            - 💝 Amigable y empática
            - ✨ Con emojis para hacerlo más ameno
            
            Da información práctica sobre:
            - Un recurso útil para su pregunta
            - Un consejo amigable
            - Un mensaje de apoyo
            
            Máximo 3-4 líneas. ¡Sé positivo y alentador!
            """
            
            response = text_generator_manager.execute_generator("gemini", prompt)
            state["response"] = response
            self._update_conversation_history(state, "GENERAL_QUERY")
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error en general_query_node: {e}")
            state["response"] = "¡Ups! 😅 No pude procesar tu consulta. ¿Me lo preguntas de otra forma? 💪"
            return state

    def _update_conversation_history(self, state: Dict[str, Any], detected_intent: str):
        """Actualiza el historial de conversación"""
        user_input = state.get("user_input", "")
        response = state.get("response", "")
        
        # Añadir mensajes al historial
        messages = state.get("messages", [])
        messages.append(HumanMessage(content=user_input))
        messages.append(AIMessage(content=response))
        state["messages"] = messages
        
        # Actualizar historial de conversación
        conversation_history = state.get("conversation_history", [])
        conversation_history.append({
            "user_input": user_input,
            "detected_intent": detected_intent,
            "response": response
        })
        state["conversation_history"] = conversation_history
