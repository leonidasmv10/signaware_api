import os
import logging
from typing import List, Union
from openai import OpenAI
from .embedding_provider import EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Proveedor de embeddings usando OpenAI."""
    
    def __init__(self, model_name: str = "text-embedding-ada-002"):
        """
        Inicializa el proveedor de embeddings de OpenAI.
        
        Args:
            model_name: Nombre del modelo de embeddings a usar
        """
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        
        # Verificar que la API key esté disponible
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.logger.error("OPENAI_API_KEY no encontrada en variables de entorno")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=api_key)
                self.logger.info(f"Proveedor de embeddings OpenAI inicializado con modelo: {model_name}")
            except Exception as e:
                self.logger.error(f"Error inicializando cliente OpenAI: {e}")
                self.client = None
    
    def get_embeddings(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Genera embeddings usando OpenAI.
        
        Args:
            text: Texto único o lista de textos para generar embeddings
            
        Returns:
            Lista de embeddings (un embedding para texto único, lista de embeddings para múltiples textos)
        """
        if not self.is_available():
            raise RuntimeError("Proveedor de embeddings OpenAI no está disponible")
        
        try:
            # Si es un solo texto, convertirlo a lista
            if isinstance(text, str):
                texts = [text]
                single_text = True
            else:
                texts = text
                single_text = False
            
            # Generar embeddings
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            
            # Extraer embeddings de la respuesta
            embeddings = [embedding.embedding for embedding in response.data]
            
            # Retornar un solo embedding si se proporcionó un solo texto
            if single_text:
                return embeddings[0]
            else:
                return embeddings
                
        except Exception as e:
            self.logger.error(f"Error generando embeddings con OpenAI: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Retorna la dimensión de los embeddings de OpenAI.
        
        Returns:
            int: Dimensión de los embeddings (1536 para text-embedding-ada-002)
        """
        # Dimensión para text-embedding-ada-002
        return 1536
    
    def is_available(self) -> bool:
        """
        Verifica si el proveedor de embeddings está disponible.
        
        Returns:
            bool: True si el proveedor está disponible y configurado correctamente
        """
        return self.client is not None and os.getenv("OPENAI_API_KEY") is not None 