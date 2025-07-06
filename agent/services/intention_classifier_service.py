import os
import time
import shutil
import numpy as np
import io
from uuid import uuid4
from signaware_api.agent.providers.text_generation.gemini_text_generation_provider import (
    GeminiTextGenerationProvider,
)


class IntentionClassifierService:
    def __init__(self):
        self.text_generation_provider = GeminiTextGenerationProvider()
        pass

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
        try:

            # Generar el prompt
            prompt = self.get_intent_prompt(user_input)

            # Generar respuesta
            response = self.text_generation_provider.execute(prompt)

            # Extraer y limpiar la respuesta
            intent = response.strip().upper()

            return intent

        except Exception as e:
            print(f"❌ Error al clasificar intención: {e}")
            return "GENERAL_QUERY"  # Categoría por defecto
