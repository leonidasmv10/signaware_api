"""
Manager para coordinar todos los agentes del sistema.
Proporciona una interfaz unificada para acceder a los diferentes agentes.
Implementa el patrón Singleton para garantizar una sola instancia.
"""

import logging
from typing import Dict, Any, Optional, Type
from .base_agent import BaseAgent
from .sound_detector_agent import SoundDetectorAgent
from .chatbot_agent import ChatbotAgent


class AgentManager:
    """
    Manager principal para coordinar todos los agentes del sistema.
    Proporciona una interfaz unificada y maneja la inicialización de agentes.
    Implementa el patrón Singleton.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implementa el patrón Singleton."""
        if cls._instance is None:
            cls._instance = super(AgentManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa el manager solo una vez."""
        if not self._initialized:
            self.logger = logging.getLogger(__name__)
            self.agents: Dict[str, BaseAgent] = {}
            self._initialize_agents()
            self._initialized = True
    
    def _initialize_agents(self):
        """Inicializa todos los agentes disponibles."""
        try:
            # Registrar agentes disponibles
            self._register_agent("sound_detector", SoundDetectorAgent())
            self._register_agent("chatbot", ChatbotAgent())
            
            self.logger.info(f"Agentes inicializados: {list(self.agents.keys())}")
            
        except Exception as e:
            self.logger.error(f"Error inicializando agentes: {e}")
            raise
    
    def _register_agent(self, name: str, agent: BaseAgent):
        """
        Registra un agente en el manager.
        
        Args:
            name: Nombre único del agente
            agent: Instancia del agente
        """
        if not isinstance(agent, BaseAgent):
            raise ValueError(f"El agente debe heredar de BaseAgent: {type(agent)}")
        
        self.agents[name] = agent
        self.logger.info(f"Agente registrado: {name} ({agent.__class__.__name__})")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """
        Obtiene un agente por nombre.
        
        Args:
            name: Nombre del agente
            
        Returns:
            BaseAgent: Instancia del agente o None si no existe
        """
        return self.agents.get(name)
    
    def execute_agent(self, agent_name: str, user_input: str, **kwargs) -> str:
        """
        Ejecuta un agente específico con validación.
        
        Args:
            agent_name: Nombre del agente a ejecutar
            user_input: Entrada del usuario
            **kwargs: Argumentos adicionales para el agente
            
        Returns:
            str: Respuesta del agente
            
        Raises:
            ValueError: Si el agente no existe
            RuntimeError: Si el agente no está inicializado
        """
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agente '{agent_name}' no encontrado. Agentes disponibles: {list(self.agents.keys())}")
        
        if not agent.is_initialized:
            raise RuntimeError(f"Agente '{agent_name}' no está inicializado correctamente")
        
        try:
            return agent.execute(user_input, **kwargs)
        except Exception as e:
            self.logger.error(f"Error ejecutando agente '{agent_name}': {e}")
            raise
    
    def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """
        Obtiene el estado de un agente específico.
        
        Args:
            agent_name: Nombre del agente
            
        Returns:
            Dict[str, Any]: Estado del agente
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return {"error": f"Agente '{agent_name}' no encontrado"}
        
        return agent.get_status()
    
    def get_all_agents_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene el estado de todos los agentes.
        
        Returns:
            Dict[str, Dict[str, Any]]: Estado de todos los agentes
        """
        return {
            name: agent.get_status() 
            for name, agent in self.agents.items()
        }
    
    def get_available_agents(self) -> list:
        """
        Obtiene la lista de agentes disponibles.
        
        Returns:
            list: Lista de nombres de agentes disponibles
        """
        return list(self.agents.keys())
    
    def is_agent_available(self, agent_name: str) -> bool:
        """
        Verifica si un agente está disponible.
        
        Args:
            agent_name: Nombre del agente
            
        Returns:
            bool: True si el agente está disponible
        """
        return agent_name in self.agents
    
    def get_manager_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado general del manager.
        
        Returns:
            Dict[str, Any]: Estado del manager
        """
        return {
            "total_agents": len(self.agents),
            "available_agents": self.get_available_agents(),
            "agents_status": self.get_all_agents_status(),
            "manager_initialized": self._initialized,
            "is_singleton": True
        }
    
    @classmethod
    def get_instance(cls):
        """
        Método de clase para obtener la instancia singleton.
        
        Returns:
            AgentManager: Instancia única del manager
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


# Instancia global del manager de agentes (Singleton)
try:
    agent_manager = AgentManager.get_instance()
except Exception as e:
    logging.error(f"Error creando instancia global del AgentManager: {e}")
    agent_manager = None 