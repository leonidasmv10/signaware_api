import os
import logging
from typing import List, Union
from langchain_huggingface import HuggingFaceEmbeddings
from .embedding_provider import EmbeddingProvider


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    """Implementación de embeddings usando HuggingFace."""

    def __init__(self, model_name: str = None):
        """
        Inicializa el proveedor de embeddings de HuggingFace.
        
        Args:
            model_name: Nombre del modelo a usar (opcional, usa variable de entorno por defecto)
        """
        self.model_name = model_name or os.getenv(
            "HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.cache_folder = os.getenv("HF_HOME_CACHE")
        self.device = os.getenv("HF_EMBEDDING_DEVICE", "cpu")
        self.logger = logging.getLogger(__name__)
        
        # Inicializar el modelo de embeddings
        try:
            self.embeddings_model = HuggingFaceEmbeddings(
                model_name=self.model_name,
                cache_folder=self.cache_folder,
                model_kwargs={"device": self.device},
            )
            self.logger.info(f"Proveedor de embeddings HuggingFace inicializado con modelo: {self.model_name}")
        except Exception as e:
            self.logger.error(f"Error inicializando modelo HuggingFace: {e}")
            self.embeddings_model = None
    
    def get_embeddings(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Genera embeddings usando HuggingFace.
        
        Args:
            text: Texto único o lista de textos para generar embeddings
            
        Returns:
            Lista de embeddings (un embedding para texto único, lista de embeddings para múltiples textos)
        """
        if not self.is_available():
            raise RuntimeError("Proveedor de embeddings HuggingFace no está disponible")
        
        try:
            # Si es un solo texto, convertirlo a lista
            if isinstance(text, str):
                texts = [text]
                single_text = True
            else:
                texts = text
                single_text = False
            
            # Generar embeddings
            embeddings = self.embeddings_model.embed_documents(texts)
            
            # Retornar un solo embedding si se proporcionó un solo texto
            if single_text:
                return embeddings[0]
            else:
                return embeddings
                
        except Exception as e:
            self.logger.error(f"Error generando embeddings con HuggingFace: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Retorna la dimensión de los embeddings de HuggingFace.
        
        Returns:
            int: Dimensión de los embeddings (384 para all-MiniLM-L6-v2)
        """
        # Dimensión para all-MiniLM-L6-v2
        return 384
    
    def is_available(self) -> bool:
        """
        Verifica si el proveedor de embeddings está disponible.
        
        Returns:
            bool: True si el proveedor está disponible y configurado correctamente
        """
        return self.embeddings_model is not None
    
    def get_embeddings_instance(self):
        """
        Retorna la instancia de HuggingFaceEmbeddings configurada.
        Método adicional para compatibilidad con código existente.
        
        Returns:
            HuggingFaceEmbeddings: Instancia del modelo de embeddings
        """
        if not self.is_available():
            raise RuntimeError("Proveedor de embeddings HuggingFace no está disponible")
        
        return self.embeddings_model 