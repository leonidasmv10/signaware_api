from .text_generation_provider import TextGenerationProvider
from openai import OpenAI
import os

class OpenAITextGenerationProvider(TextGenerationProvider):
    """
    Provider para generación de texto usando OpenAI API v1.0.0.
    """
    
    def __init__(self, model_name="gpt-3.5-turbo"):
        """
        Inicializa el provider de OpenAI.
        
        Args:
            model_name: Nombre del modelo a usar
        """
        self.model_name = model_name
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def execute(self, prompt):
        """
        Ejecuta la generación de texto usando OpenAI.
        
        Args:
            prompt: Prompt para generar texto
            
        Returns:
            str: Respuesta generada por el modelo
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.7,
            )
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error en OpenAI API: {str(e)}") 