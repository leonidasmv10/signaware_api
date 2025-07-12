"""
Módulo para providers de búsqueda web en tiempo real.
"""

from .web_search_provider import WebSearchProvider, web_search_provider
from .medical_news_provider import MedicalNewsProvider, medical_news_provider

__all__ = [
    'WebSearchProvider', 
    'web_search_provider',
    'MedicalNewsProvider',
    'medical_news_provider'
] 