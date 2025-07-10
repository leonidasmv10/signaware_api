"""
Nodos del agente de audio inteligente para Signaware.
Cada nodo representa una etapa del procesamiento de audio.
"""

import os
import logging
import tempfile
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

# Configurar logging
logger = logging.getLogger(__name__)


class ChatbotNodes:

    def __init__(self):
        """Inicializa los nodos y sus dependencias."""
        self.logger = logging.getLogger(__name__)
