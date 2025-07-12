"""
Provider para búsqueda de noticias médicas actualizadas sobre audífonos y salud auditiva.
"""

import requests
import logging
from typing import Dict, Any
import os
from datetime import datetime, timedelta

class MedicalNewsProvider:
    """Provider para obtener noticias médicas actualizadas"""
    
    # Configuración de tiempo de búsqueda (en días)
    DEFAULT_SEARCH_DAYS = 30  # 30 días por defecto (límite del plan gratuito de News API)
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_latest_hearing_aid_news(self, days: int = None) -> Dict[str, Any]:
        """
        Obtiene las últimas noticias sobre audífonos y salud auditiva.
        
        Args:
            days: Número de días hacia atrás para buscar
            
        Returns:
            Dict con noticias encontradas
        """
        return self._get_news_with_fallback(
            query="audífonos OR hearing aids OR audiología OR otorrinolaringología OR pérdida auditiva OR audición OR oído OR sordera OR hipoacusia OR implante coclear OR audiólogo OR otorrino OR tecnología auditiva OR hearing technology OR audiology",
            keywords=["audífono", "hearing", "audiología", "otorrino", "audición", "oído", "sordera", "hipoacusia", "implante", "audiólogo", "audiology", "hearing aids", "hearing technology", "tecnología auditiva", "pérdida auditiva"],
            days=days,
            topic="audífonos"
        )
    
    def get_medical_research_news(self, days: int = None) -> Dict[str, Any]:
        """Obtiene noticias de investigación médica en audición"""
        return self._get_news_with_fallback(
            query="investigación audición OR hearing research OR estudio auditivo OR medical research hearing OR audiology research",
            keywords=["investigación", "research", "estudio", "medical", "audición", "hearing"],
            days=days,
            topic="investigación en audición"
        )
    
    def get_medical_technology_news(self, days: int = None) -> Dict[str, Any]:
        """Obtiene noticias de tecnología médica en audición"""
        return self._get_news_with_fallback(
            query="tecnología audífonos OR hearing technology OR innovación auditiva OR medical technology hearing",
            keywords=["tecnología", "technology", "innovación", "innovation", "audífono", "hearing"],
            days=days,
            topic="tecnología en audición"
        )
    
    def _get_news_with_fallback(self, query: str, keywords: list, days: int = None, topic: str = "audífonos") -> Dict[str, Any]:
        """Método centralizado para obtener noticias con fallback"""
        try:
            # Usar el valor por defecto si no se especifica
            if days is None:
                days = self.DEFAULT_SEARCH_DAYS
            
            # Verificar API key
            news_api_key = os.getenv("NEWS_API_KEY")
            if not news_api_key:
                self.logger.error("❌ News API key NO encontrada en variables de entorno")
                return {
                    "error": "News API key not found",
                    "message": "La API key de News API no está configurada. Agrega NEWS_API_KEY a tus variables de entorno."
                }
            
            # Probar la API key
            if not self._test_news_api(news_api_key):
                return {
                    "error": "News API key invalid",
                    "message": "La API key de News API no es válida o no tiene permisos. Verifica tu configuración."
                }
            
            # Buscar noticias
            result = self._search_news_api(query, days, news_api_key)
            self.logger.info(f"📰 Noticias encontradas en News API: {result.get('total_results', 0)}")
            
            if result.get("total_results", 0) > 0:
                # Filtrar noticias relevantes
                relevant_articles = [
                    article for article in result.get("articles", [])
                    if any(keyword in article.get("title", "").lower() or 
                           keyword in article.get("description", "").lower()
                           for keyword in keywords)
                ]
                
                self.logger.info(f"📰 Artículos relevantes después del filtro: {len(relevant_articles)}")
                
                if relevant_articles:
                    result["articles"] = relevant_articles[:5]
                    result["total_results"] = len(relevant_articles)
                    self.logger.info("✅ Devolviendo noticias reales de News API")
                    return result
            
            # No usar fallback, devolver error claro
            self.logger.info("🔍 No se encontraron noticias en News API")
            
            return {
                "error": "No relevant news found",
                "message": f"No se encontraron noticias específicas sobre {topic} en los últimos {days} días. Esto es normal porque las noticias sobre audífonos no son tan frecuentes como otros temas médicos."
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo noticias: {e}")
            return {
                "error": "News API error",
                "message": "Error al obtener noticias. Verifica tu conexión a internet y la configuración de la API."
            }
    
    def _search_news_api(self, query: str, days: int, api_key: str) -> Dict[str, Any]:
        """Busca usando News API"""
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'from': from_date,
                'language': 'es',
                'sortBy': 'publishedAt',
                'apiKey': api_key,
                'pageSize': 10
            }
            
            response = self.session.get(url, params=params)
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                return {
                    "source": "News API",
                    "total_results": len(articles),
                    "articles": [
                        {
                            "title": article.get('title', ''),
                            "description": article.get('description', ''),
                            "url": article.get('url', ''),
                            "published_at": article.get('publishedAt', ''),
                            "source": article.get('source', {}).get('name', '')
                        }
                        for article in articles[:5]
                    ]
                }
            else:
                raise Exception(f"News API error: {data.get('message', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Error en News API search: {e}")
            raise
    


    def _test_news_api(self, api_key: str) -> bool:
        """Prueba si la API key de News API funciona correctamente"""
        try:
            self.logger.info("🔍 Probando News API key...")
            
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'country': 'es',
                'apiKey': api_key,
                'pageSize': 1
            }
            
            response = self.session.get(url, params=params)
            data = response.json()
            
            if data.get('status') == 'ok':
                self.logger.info("✅ News API key funciona correctamente")
                return True
            elif data.get('status') == 'error':
                self.logger.error(f"❌ News API key error: {data.get('message', 'Sin mensaje de error')}")
                return False
            else:
                self.logger.error(f"❌ News API error: {data.get('status')}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error probando News API: {e}")
            return False
    
    def get_medical_trends(self) -> str:
        """Obtiene tendencias actuales en salud auditiva"""
        trends = [
            "🎧 **Audífonos con IA**: Control automático de ruido y adaptación personalizada",
            "📱 **Conectividad Total**: Integración con smartphones y dispositivos inteligentes",
            "🔋 **Baterías Recargables**: Mayor duración y menos residuos",
            "🎯 **Personalización Avanzada**: Ajustes específicos para cada tipo de pérdida auditiva",
            "🌍 **Sostenibilidad**: Materiales eco-friendly y packaging reciclable"
        ]
        
        return "\n".join(trends[:3])
    
    def get_medical_advice_by_topic(self, topic: str) -> str:
        """Obtiene consejos médicos específicos por tema"""
        advice_database = {
            "adaptación": {
                "title": "🎧 Proceso de Adaptación a Audífonos",
                "tips": [
                    "• La adaptación puede tomar 2-4 semanas",
                    "• Comienza con volúmenes bajos",
                    "• Practica en entornos tranquilos primero",
                    "• Mantén un diario de progreso"
                ]
            },
            "mantenimiento": {
                "title": "🔧 Mantenimiento de Audífonos",
                "tips": [
                    "• Limpia diariamente con paño suave",
                    "• Evita la humedad y el agua",
                    "• Revisa las pilas regularmente",
                    "• Guarda en estuche seco por la noche"
                ]
            },
            "precios": {
                "title": "💰 Información de Precios",
                "tips": [
                    "• Rango: 500-3000€ según tecnología",
                    "• Consulta con varios centros",
                    "• Pregunta por financiación",
                    "• Algunos seguros cubren parte del coste"
                ]
            },
            "tecnología": {
                "title": "📱 Tecnología Moderna",
                "tips": [
                    "• Bluetooth para smartphones",
                    "• Control de ruido automático",
                    "• Aplicaciones de ajuste remoto",
                    "• Baterías recargables disponibles"
                ]
            }
        }
        
        topic_lower = topic.lower()
        for key, value in advice_database.items():
            if key in topic_lower or topic_lower in key:
                return f"{value['title']}\n" + "\n".join(value['tips'])
        
        return "💡 Consulta con un especialista para consejos personalizados según tu caso específico."

# Instancia global
medical_news_provider = MedicalNewsProvider() 