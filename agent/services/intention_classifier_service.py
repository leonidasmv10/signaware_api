import os
import time
import shutil
import numpy as np
import io
from uuid import uuid4
from agent.providers.text_generation.text_generator_manager import (
    text_generator_manager,
)


class IntentionClassifierService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IntentionClassifierService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.text_generator_manager = text_generator_manager
            self._initialized = True

    def get_intent_prompt(self, user_input):
        """Genera el prompt para clasificar la intención del usuario"""
        return f"""
    Eres un asistente que clasifica intenciones para ayudar a personas con discapacidad auditiva.

    Clasifica la siguiente consulta del usuario en una de estas categorías:

    - HEARING_AIDS: Consultas sobre audífonos, precios, tecnología, mantenimiento, consejos sobre audífonos, información general sobre audífonos
    - MEDICAL_CENTER: Buscar centros médicos, especialistas, hospitales, clínicas, citas médicas, ubicaciones, dónde encontrar ayuda
    - MEDICAL_NEWS: Noticias médicas, actualidad, novedades, avances, investigación, tendencias, últimos avances, innovaciones, estudios recientes
    - GENERATE_IMAGE: Generar imágenes, crear imágenes, dibujos
    - SOUND_REPORT: Reportes de sonidos, análisis de audio, detección de sonidos
    - GENERAL_QUERY: Otras consultas generales

    Reglas de prioridad (en orden de importancia):
    1. Si la consulta menciona "noticias", "actualidad", "novedades", "avances", "últimos avances", "innovaciones", "investigación", "tendencias", "estudios recientes" → MEDICAL_NEWS
    2. Si la consulta menciona "buscar", "encontrar", "dónde", "centros", "especialistas", "hospitales", "clínicas", "ubicaciones" → MEDICAL_CENTER
    3. Si la consulta es sobre audífonos pero NO busca centros ni noticias → HEARING_AIDS
    4. Si la consulta busca ubicaciones o direcciones → MEDICAL_CENTER

    Ejemplos:
    - "¿Cuáles son los últimos avances en audífonos?" → MEDICAL_NEWS
    - "Quiero noticias sobre audífonos" → MEDICAL_NEWS
    - "Buscar centros médicos en Barcelona" → MEDICAL_CENTER
    - "¿Cómo funcionan los audífonos?" → HEARING_AIDS

    Consulta del usuario: "{user_input}"

    Responde SOLO con una de las categorías.
    No respondas nada más, solo la categoría exacta sin explicaciones.
    """

    def execute(self, user_input):
        try:

            # Generar el prompt
            prompt = self.get_intent_prompt(user_input)

            # Generar respuesta
            response = self.text_generator_manager.execute_generator("gemini", prompt)

            # Extraer y limpiar la respuesta
            intent = response.strip().upper()

            return intent

        except Exception as e:
            print(f"❌ Error al clasificar intención: {e}")
            return "GENERAL_QUERY"  # Categoría por defecto
