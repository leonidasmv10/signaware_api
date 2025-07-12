"""
Manager para coordinar todos los generadores de imágenes.
Proporciona una interfaz unificada para acceder a los diferentes generadores de imágenes.
Implementa el patrón Singleton para garantizar una sola instancia.
"""

import logging
from typing import Dict, Any, Optional
from .image_generation_provider import ImageGenerationProvider
from .stable_diffusion_provider import StableDiffusionProvider


class ImageGeneratorManager:
    """
    Manager principal para coordinar todos los generadores de imágenes.
    Proporciona una interfaz unificada y maneja la inicialización de generadores.
    Implementa el patrón Singleton.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implementa el patrón Singleton."""
        if cls._instance is None:
            cls._instance = super(ImageGeneratorManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa el manager solo una vez."""
        if not self._initialized:
            self.logger = logging.getLogger(__name__)
            self.generators: Dict[str, ImageGenerationProvider] = {}
            self._initialize_generators()
            self._initialized = True
    
    def _initialize_generators(self):
        """Inicializa todos los generadores de imágenes disponibles."""
        try:
            # Registrar generadores disponibles
            self._register_generator("stable_diffusion", StableDiffusionProvider())
            
            self.logger.info(f"Generadores de imágenes inicializados: {list(self.generators.keys())}")
            
        except Exception as e:
            self.logger.error(f"Error inicializando generadores de imágenes: {e}")
            raise
    
    def _register_generator(self, name: str, generator: ImageGenerationProvider):
        """
        Registra un generador en el manager.
        
        Args:
            name: Nombre único del generador
            generator: Instancia del generador
        """
        if not isinstance(generator, ImageGenerationProvider):
            raise ValueError(f"El generador debe heredar de ImageGenerationProvider: {type(generator)}")
        
        self.generators[name] = generator
        self.logger.info(f"Generador de imágenes registrado: {name} ({generator.__class__.__name__})")
    
    def get_generator(self, name: str) -> Optional[ImageGenerationProvider]:
        """
        Obtiene un generador por nombre.
        
        Args:
            name: Nombre del generador
            
        Returns:
            ImageGenerationProvider: Instancia del generador o None si no existe
        """
        return self.generators.get(name)
    
    def is_generator_available(self, name: str) -> bool:
        """
        Verifica si un generador está disponible.
        
        Args:
            name: Nombre del generador
            
        Returns:
            bool: True si está disponible, False en caso contrario
        """
        generator = self.get_generator(name)
        return generator is not None and generator.is_available()
    
    def execute_generator(self, name: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta un generador específico.
        
        Args:
            name: Nombre del generador
            prompt: Prompt para generar la imagen
            **kwargs: Parámetros adicionales
            
        Returns:
            Dict con la imagen generada y metadatos
        """
        generator = self.get_generator(name)
        if generator is None:
            raise ValueError(f"Generador '{name}' no encontrado")
        
        if not generator.is_available():
            raise RuntimeError(f"Generador '{name}' no está disponible")
        
        return generator.execute(prompt, **kwargs)
    
    def execute_with_fallback(self, primary_generator: str, prompt: str, fallback_generators: list = None) -> Dict[str, Any]:
        """
        Ejecuta un generador con fallback a otros generadores si falla.
        
        Args:
            primary_generator: Generador principal a usar
            prompt: Prompt para generar imagen
            fallback_generators: Lista de generadores de respaldo
            
        Returns:
            Dict con la imagen generada del primer generador exitoso
        """
        if fallback_generators is None:
            fallback_generators = ["stable_diffusion"]
        
        # Intentar generador principal
        try:
            return self.execute_generator(primary_generator, prompt)
        except Exception as e:
            self.logger.warning(f"Generador principal '{primary_generator}' falló: {e}")
        
        # Intentar generadores de fallback
        for fallback_generator in fallback_generators:
            if fallback_generator != primary_generator and self.is_generator_available(fallback_generator):
                try:
                    self.logger.info(f"Intentando generador de fallback: {fallback_generator}")
                    return self.execute_generator(fallback_generator, prompt)
                except Exception as e:
                    self.logger.warning(f"Generador de fallback '{fallback_generator}' falló: {e}")
        
        # Si todos fallan, devolver error
        raise RuntimeError(f"Todos los generadores de imágenes fallaron: {primary_generator}, {fallback_generators}")
    
    def get_available_generators(self) -> list:
        """
        Obtiene la lista de generadores disponibles.
        
        Returns:
            list: Lista de nombres de generadores disponibles
        """
        return [name for name, generator in self.generators.items() if generator.is_available()]
    
    @classmethod
    def get_instance(cls):
        """
        Método de clase para obtener la instancia singleton.
        
        Returns:
            ImageGeneratorManager: Instancia única del manager
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# Instancia global del manager
image_generator_manager = ImageGeneratorManager.get_instance() 