"""
Clase base para proveedores de generación de imágenes.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ImageGenerationProvider(ABC):
    """
    Clase base para proveedores de generación de imágenes.
    Define la interfaz común para todos los proveedores de imágenes.
    """
    
    @abstractmethod
    def execute(self, prompt: str, negative_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Genera una imagen basada en el prompt proporcionado.
        
        Args:
            prompt: Descripción de la imagen a generar
            negative_prompt: Descripción de lo que NO debe aparecer en la imagen
            **kwargs: Parámetros adicionales específicos del proveedor
            
        Returns:
            Dict con la imagen generada y metadatos
        """
        raise NotImplementedError("Debes implementar este método en la subclase.")
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica si el proveedor está disponible para usar.
        
        Returns:
            bool: True si está disponible, False en caso contrario
        """
        raise NotImplementedError("Debes implementar este método en la subclase.") 