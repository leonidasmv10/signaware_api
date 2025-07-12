from abc import ABC, abstractmethod
from typing import List, Union


class EmbeddingProvider(ABC):
    """Clase base abstracta para proveedores de embeddings."""

    @abstractmethod
    def get_embeddings(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Genera embeddings para el texto proporcionado.
        
        Args:
            text: Texto único o lista de textos para generar embeddings
            
        Returns:
            Lista de embeddings (un embedding para texto único, lista de embeddings para múltiples textos)
        """
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """
        Retorna la dimensión de los embeddings generados por este proveedor.
        
        Returns:
            int: Dimensión de los embeddings
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica si el proveedor de embeddings está disponible.
        
        Returns:
            bool: True si el proveedor está disponible y configurado correctamente
        """
        pass 