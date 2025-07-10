"""
Clase base para todos los agentes del sistema.
Define la interfaz común que deben implementar todos los agentes.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAgent(ABC):
    """
    Clase base abstracta para todos los agentes del sistema.
    Define la interfaz común y métodos base que todos los agentes deben implementar.
    """
    
    def __init__(self):
        """Inicializa el agente base."""
        self.name = self.__class__.__name__
        self.is_initialized = False
        self._initialize_agent()
    
    def _initialize_agent(self):
        """
        Inicializa el agente y sus componentes.
        Este método debe ser implementado por las subclases.
        """
        try:
            self._setup_components()
            self.is_initialized = True
        except Exception as e:
            self.is_initialized = False
            raise RuntimeError(f"Error inicializando agente {self.name}: {e}")
    
    @abstractmethod
    def _setup_components(self):
        """
        Configura los componentes específicos del agente.
        Debe ser implementado por las subclases.
        """
        pass
    
    @abstractmethod
    def execute(self, user_input: str, **kwargs) -> str:
        """
        Ejecuta el agente con la entrada del usuario.
        
        Args:
            user_input: Entrada del usuario
            **kwargs: Argumentos adicionales específicos del agente
            
        Returns:
            str: Respuesta del agente
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del agente.
        
        Returns:
            Dict[str, Any]: Información del estado del agente
        """
        return {
            "name": self.name,
            "is_initialized": self.is_initialized,
            "type": self.__class__.__name__
        }
    
    def validate_input(self, user_input: str) -> bool:
        """
        Valida la entrada del usuario.
        
        Args:
            user_input: Entrada del usuario a validar
            
        Returns:
            bool: True si la entrada es válida, False en caso contrario
        """
        return user_input is not None and len(user_input.strip()) > 0
    
    def preprocess_input(self, user_input: str) -> str:
        """
        Preprocesa la entrada del usuario antes de la ejecución.
        
        Args:
            user_input: Entrada del usuario
            
        Returns:
            str: Entrada preprocesada
        """
        return user_input.strip() if user_input else ""
    
    def postprocess_output(self, output: str) -> str:
        """
        Postprocesa la salida del agente antes de devolverla.
        
        Args:
            output: Salida del agente
            
        Returns:
            str: Salida postprocesada
        """
        return output.strip() if output else ""
    
    def execute_with_validation(self, user_input: str, **kwargs) -> str:
        """
        Ejecuta el agente con validación completa de entrada y salida.
        
        Args:
            user_input: Entrada del usuario
            **kwargs: Argumentos adicionales
            
        Returns:
            str: Respuesta procesada del agente
        """
        if not self.is_initialized:
            raise RuntimeError(f"Agente {self.name} no está inicializado correctamente")
        
        if not self.validate_input(user_input):
            raise ValueError("Entrada del usuario inválida")
        
        # Preprocesar entrada
        processed_input = self.preprocess_input(user_input)
        
        # Ejecutar agente
        raw_output = self.execute(processed_input, **kwargs)
        
        # Postprocesar salida
        final_output = self.postprocess_output(raw_output)
        
        return final_output 