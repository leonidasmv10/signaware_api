import os
import time
import shutil
import numpy as np
import io
from uuid import uuid4
from ..providers.text_generation.text_generator_manager import text_generator_manager


class IntentionClassifierService:
    """
    Servicio para clasificar las intenciones del usuario.
    Utiliza el TextGeneratorManager singleton para acceder a los generadores de texto.
    """
    
    def __init__(self):
        """Inicializa el servicio usando el manager singleton."""
        self.text_generator_manager = text_generator_manager
        self.default_generator = "gemini"  # Generador por defecto
        self.fallback_generators = ["openai"]  # Generadores de respaldo
        
        # Verificar que el manager esté disponible
        if self.text_generator_manager is None:
            raise RuntimeError("TextGeneratorManager no está disponible")

    def get_intent_prompt(self, user_input):
        """Genera el prompt para clasificar la intención del usuario"""
        return f"""
    Eres un asistente que clasifica intenciones para ayudar a personas con discapacidad auditiva.

    Clasifica la siguiente consulta del usuario en una de estas categorías:
    - HEARING_AIDS
    - VISUAL_SIGNALS
    - AUDIO_TRANSLATION
    - GENERATE_IMAGE
    - MEDICAL_CENTER
    - RECOMMEND_APP
    - KNOW_RIGHTS
    - CERTIFICATE
    - SOUND_REPORT
    - GENERAL_QUERY

    Consulta del usuario: "{user_input}"

    Responde SOLO con una de las categorías.
    No respondas nada más, solo la categoría exacta sin explicaciones.
    """

    def execute(self, user_input):
        """
        Ejecuta la clasificación de intención usando el manager singleton.
        
        Args:
            user_input: Entrada del usuario a clasificar
            
        Returns:
            str: Categoría de intención clasificada
        """
        try:
            # Generar el prompt
            prompt = self.get_intent_prompt(user_input)

            # Usar el manager singleton con fallback automático
            response = self.text_generator_manager.execute_with_fallback(
                primary_generator=self.default_generator,
                prompt=prompt,
                fallback_generators=self.fallback_generators
            )

            # Extraer y limpiar la respuesta
            intent = response.strip().upper()

            return intent

        except Exception as e:
            print(f"❌ Error al clasificar intención: {e}")
            return "GENERAL_QUERY"  # Categoría por defecto
    
    def execute_with_specific_generator(self, user_input, generator_name="gemini"):
        """
        Ejecuta la clasificación usando un generador específico.
        
        Args:
            user_input: Entrada del usuario a clasificar
            generator_name: Nombre del generador a usar
            
        Returns:
            str: Categoría de intención clasificada
        """
        try:
            # Generar el prompt
            prompt = self.get_intent_prompt(user_input)

            # Usar el generador específico
            response = self.text_generator_manager.execute_generator(
                generator_name=generator_name,
                prompt=prompt
            )

            # Extraer y limpiar la respuesta
            intent = response.strip().upper()

            return intent

        except Exception as e:
            print(f"❌ Error al clasificar intención con {generator_name}: {e}")
            return "GENERAL_QUERY"  # Categoría por defecto
    
    def get_service_status(self):
        """
        Obtiene el estado del servicio de clasificación de intenciones.
        
        Returns:
            dict: Estado del servicio
        """
        return {
            "service_name": "IntentionClassifierService",
            "text_generator_manager_available": self.text_generator_manager is not None,
            "default_generator": self.default_generator,
            "fallback_generators": self.fallback_generators,
            "available_generators": self.text_generator_manager.get_available_generators() if self.text_generator_manager else []
        }
