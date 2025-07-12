"""
Manager para coordinar todos los proveedores de embeddings.
Proporciona una interfaz unificada para acceder a los diferentes proveedores de embeddings.
Implementa el patrón Singleton para garantizar una sola instancia.
"""

import logging
from typing import Dict, Any, Optional, Union, List
from .embedding_provider import EmbeddingProvider
from .openai_embedding_provider import OpenAIEmbeddingProvider
from .huggingface_embedding_provider import HuggingFaceEmbeddingProvider


class EmbeddingManager:
    """
    Manager principal para coordinar todos los proveedores de embeddings.
    Proporciona una interfaz unificada y maneja la inicialización de proveedores.
    Implementa el patrón Singleton.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implementa el patrón Singleton."""
        if cls._instance is None:
            cls._instance = super(EmbeddingManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa el manager solo una vez."""
        if not self._initialized:
            self.logger = logging.getLogger(__name__)
            self.providers: Dict[str, EmbeddingProvider] = {}
            self._initialize_providers()
            self._initialized = True
    
    def _initialize_providers(self):
        """Inicializa todos los proveedores de embeddings disponibles."""
        try:
            # Registrar proveedores disponibles
            self._register_provider("openai", OpenAIEmbeddingProvider())
            
            # HuggingFace puede requerir más recursos, inicializarlo solo si es necesario
            try:
                self._register_provider("huggingface", HuggingFaceEmbeddingProvider())
                self.logger.info("Proveedor HuggingFace inicializado exitosamente")
            except Exception as e:
                self.logger.warning(f"No se pudo inicializar HuggingFace provider: {e}")
            
            self.logger.info(f"Proveedores de embeddings inicializados: {list(self.providers.keys())}")
            
        except Exception as e:
            self.logger.error(f"Error inicializando proveedores de embeddings: {e}")
            raise
    
    def _register_provider(self, name: str, provider: EmbeddingProvider):
        """
        Registra un proveedor en el manager.
        
        Args:
            name: Nombre único del proveedor
            provider: Instancia del proveedor
        """
        if not isinstance(provider, EmbeddingProvider):
            raise ValueError(f"El proveedor debe heredar de EmbeddingProvider: {type(provider)}")
        
        self.providers[name] = provider
        self.logger.info(f"Proveedor de embeddings registrado: {name} ({provider.__class__.__name__})")
    
    def get_provider(self, name: str) -> Optional[EmbeddingProvider]:
        """
        Obtiene un proveedor por nombre.
        
        Args:
            name: Nombre del proveedor
            
        Returns:
            EmbeddingProvider: Instancia del proveedor o None si no existe
        """
        return self.providers.get(name)
    
    def get_embeddings(self, provider_name: str, text: Union[str, List[str]], **kwargs) -> Union[List[float], List[List[float]]]:
        """
        Genera embeddings usando un proveedor específico.
        
        Args:
            provider_name: Nombre del proveedor a usar
            text: Texto único o lista de textos para generar embeddings
            **kwargs: Argumentos adicionales para el proveedor
            
        Returns:
            Lista de embeddings (un embedding para texto único, lista de embeddings para múltiples textos)
            
        Raises:
            ValueError: Si el proveedor no existe
            RuntimeError: Si el proveedor no está disponible
        """
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Proveedor '{provider_name}' no encontrado. Proveedores disponibles: {list(self.providers.keys())}")
        
        if not provider.is_available():
            raise RuntimeError(f"Proveedor '{provider_name}' no está disponible")
        
        try:
            return provider.get_embeddings(text)
        except Exception as e:
            self.logger.error(f"Error generando embeddings con proveedor '{provider_name}': {e}")
            raise
    
    def get_provider_status(self, provider_name: str) -> Dict[str, Any]:
        """
        Obtiene el estado de un proveedor específico.
        
        Args:
            provider_name: Nombre del proveedor
            
        Returns:
            Dict[str, Any]: Estado del proveedor
        """
        provider = self.get_provider(provider_name)
        if not provider:
            return {"error": f"Proveedor '{provider_name}' no encontrado"}
        
        return {
            "name": provider_name,
            "type": provider.__class__.__name__,
            "available": provider.is_available(),
            "embedding_dimension": provider.get_embedding_dimension() if provider.is_available() else None
        }
    
    def get_all_providers_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene el estado de todos los proveedores.
        
        Returns:
            Dict[str, Dict[str, Any]]: Estado de todos los proveedores
        """
        return {
            name: self.get_provider_status(name)
            for name in self.providers.keys()
        }
    
    def get_available_providers(self) -> list:
        """
        Obtiene la lista de proveedores disponibles.
        
        Returns:
            list: Lista de nombres de proveedores disponibles
        """
        return [name for name, provider in self.providers.items() if provider.is_available()]
    
    def is_provider_available(self, provider_name: str) -> bool:
        """
        Verifica si un proveedor está disponible.
        
        Args:
            provider_name: Nombre del proveedor
            
        Returns:
            bool: True si el proveedor está disponible
        """
        provider = self.get_provider(provider_name)
        return provider is not None and provider.is_available()
    
    def get_manager_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado general del manager.
        
        Returns:
            Dict[str, Any]: Estado del manager
        """
        return {
            "total_providers": len(self.providers),
            "available_providers": self.get_available_providers(),
            "providers_status": self.get_all_providers_status(),
            "manager_initialized": self._initialized,
            "is_singleton": True
        }
    
    def get_embeddings_with_fallback(self, primary_provider: str, text: Union[str, List[str]], fallback_providers: list = None) -> Union[List[float], List[List[float]]]:
        """
        Genera embeddings con fallback a otros proveedores si falla.
        
        Args:
            primary_provider: Proveedor principal a usar
            text: Texto único o lista de textos para generar embeddings
            fallback_providers: Lista de proveedores de respaldo
            
        Returns:
            Lista de embeddings del primer proveedor exitoso
        """
        if fallback_providers is None:
            fallback_providers = ["openai", "huggingface"]
        
        # Intentar proveedor principal
        try:
            return self.get_embeddings(primary_provider, text)
        except Exception as e:
            self.logger.warning(f"Proveedor principal '{primary_provider}' falló: {e}")
        
        # Intentar proveedores de fallback
        for fallback_provider in fallback_providers:
            if fallback_provider != primary_provider:
                try:
                    return self.get_embeddings(fallback_provider, text)
                except Exception as e:
                    self.logger.warning(f"Proveedor de fallback '{fallback_provider}' falló: {e}")
        
        # Si todos fallan, lanzar excepción
        raise RuntimeError(f"Todos los proveedores de embeddings fallaron: {[primary_provider] + fallback_providers}")
    
    @classmethod
    def get_instance(cls):
        """
        Obtiene la instancia singleton del manager.
        
        Returns:
            EmbeddingManager: Instancia única del manager
        """
        return cls()
    
    @classmethod
    def reset_instance(cls):
        """
        Resetea la instancia singleton (útil para testing).
        """
        cls._instance = None
        cls._initialized = False 