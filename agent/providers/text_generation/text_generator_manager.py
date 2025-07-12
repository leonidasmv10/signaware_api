"""
Manager para coordinar todos los generadores de texto.
Proporciona una interfaz unificada para acceder a los diferentes generadores de texto.
Implementa el patrón Singleton para garantizar una sola instancia.
"""

import logging
from typing import Dict, Any, Optional
from .text_generation_provider import TextGenerationProvider
from .gemini_text_generation_provider import GeminiTextGenerationProvider
from .openai_text_generation_provider import OpenAITextGenerationProvider
from .leonidasmv_text_generation_provider import LeonidasmvTextGenerationProvider


class TextGeneratorManager:
    """
    Manager principal para coordinar todos los generadores de texto.
    Proporciona una interfaz unificada y maneja la inicialización de generadores.
    Implementa el patrón Singleton.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implementa el patrón Singleton."""
        if cls._instance is None:
            cls._instance = super(TextGeneratorManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa el manager solo una vez."""
        if not self._initialized:
            self.logger = logging.getLogger(__name__)
            self.generators: Dict[str, TextGenerationProvider] = {}
            self._initialize_generators()
            self._initialized = True
    
    def _initialize_generators(self):
        """Inicializa todos los generadores de texto disponibles."""
        try:
            # Registrar generadores disponibles
            self._register_generator("gemini", GeminiTextGenerationProvider())
            self._register_generator("openai", OpenAITextGenerationProvider())
            
            # Leonidasmv puede requerir más recursos, inicializarlo solo si es necesario
            try:
                # self._register_generator("leonidasmv", LeonidasmvTextGenerationProvider())
                self.logger.info("Generador Leonidasmv inicializado exitosamente")
            except Exception as e:
                self.logger.warning(f"No se pudo inicializar Leonidasmv generator: {e}")
            
            self.logger.info(f"Generadores inicializados: {list(self.generators.keys())}")
            
        except Exception as e:
            self.logger.error(f"Error inicializando generadores: {e}")
            raise
    
    def _register_generator(self, name: str, generator: TextGenerationProvider):
        """
        Registra un generador en el manager.
        
        Args:
            name: Nombre único del generador
            generator: Instancia del generador
        """
        if not isinstance(generator, TextGenerationProvider):
            raise ValueError(f"El generador debe heredar de TextGenerationProvider: {type(generator)}")
        
        self.generators[name] = generator
        self.logger.info(f"Generador registrado: {name} ({generator.__class__.__name__})")
    
    def get_generator(self, name: str) -> Optional[TextGenerationProvider]:
        """
        Obtiene un generador por nombre.
        
        Args:
            name: Nombre del generador
            
        Returns:
            TextGenerationProvider: Instancia del generador o None si no existe
        """
        return self.generators.get(name)
    
    def execute_generator(self, generator_name: str, prompt: str, **kwargs) -> str:
        """
        Ejecuta un generador específico con validación.
        
        Args:
            generator_name: Nombre del generador a ejecutar
            prompt: Prompt para generar texto
            **kwargs: Argumentos adicionales para el generador
            
        Returns:
            str: Respuesta generada por el generador
            
        Raises:
            ValueError: Si el generador no existe
            RuntimeError: Si el generador no está inicializado
        """
        generator = self.get_generator(generator_name)
        if not generator:
            raise ValueError(f"Generador '{generator_name}' no encontrado. Generadores disponibles: {list(self.generators.keys())}")
        
        try:
            return generator.execute(prompt)
        except Exception as e:
            self.logger.error(f"Error ejecutando generador '{generator_name}': {e}")
            raise
    
    def get_generator_status(self, generator_name: str) -> Dict[str, Any]:
        """
        Obtiene el estado de un generador específico.
        
        Args:
            generator_name: Nombre del generador
            
        Returns:
            Dict[str, Any]: Estado del generador
        """
        generator = self.get_generator(generator_name)
        if not generator:
            return {"error": f"Generador '{generator_name}' no encontrado"}
        
        return {
            "name": generator_name,
            "type": generator.__class__.__name__,
            "available": True
        }
    
    def get_all_generators_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene el estado de todos los generadores.
        
        Returns:
            Dict[str, Dict[str, Any]]: Estado de todos los generadores
        """
        return {
            name: self.get_generator_status(name)
            for name in self.generators.keys()
        }
    
    def get_available_generators(self) -> list:
        """
        Obtiene la lista de generadores disponibles.
        
        Returns:
            list: Lista de nombres de generadores disponibles
        """
        return list(self.generators.keys())
    
    def is_generator_available(self, generator_name: str) -> bool:
        """
        Verifica si un generador está disponible.
        
        Args:
            generator_name: Nombre del generador
            
        Returns:
            bool: True si el generador está disponible
        """
        return generator_name in self.generators
    
    def get_manager_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado general del manager.
        
        Returns:
            Dict[str, Any]: Estado del manager
        """
        return {
            "total_generators": len(self.generators),
            "available_generators": self.get_available_generators(),
            "generators_status": self.get_all_generators_status(),
            "manager_initialized": self._initialized,
            "is_singleton": True
        }
    
    def execute_with_fallback(self, primary_generator: str, prompt: str, fallback_generators: list = None) -> str:
        """
        Ejecuta un generador con fallback a otros generadores si falla.
        
        Args:
            primary_generator: Generador principal a usar
            prompt: Prompt para generar texto
            fallback_generators: Lista de generadores de respaldo
            
        Returns:
            str: Respuesta del primer generador exitoso
        """
        if fallback_generators is None:
            fallback_generators = ["gemini", "openai"]
        
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
        raise RuntimeError(f"Todos los generadores fallaron: {primary_generator}, {fallback_generators}")
    
    @classmethod
    def get_instance(cls):
        """
        Método de clase para obtener la instancia singleton.
        
        Returns:
            TextGeneratorManager: Instancia única del manager
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """
        Método de clase para resetear la instancia singleton (útil para testing).
        """
        cls._instance = None
        cls._initialized = False


# Instancia global del manager de generadores de texto (Singleton)
try:
    text_generator_manager = TextGeneratorManager.get_instance()
except Exception as e:
    logging.error(f"Error creando instancia global del TextGeneratorManager: {e}")
    text_generator_manager = None 