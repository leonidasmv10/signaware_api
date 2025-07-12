"""
Provider para búsqueda web en tiempo real.
Permite buscar información actualizada de centros médicos y especialistas.
"""

import requests
import logging
from typing import Dict, Any, List, Optional
import os

class WebSearchProvider:
    """Provider para búsqueda web en tiempo real"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_medical_centers(self, location: str = None, specialty: str = "audífonos") -> Dict[str, Any]:
        """
        Busca centros médicos especializados más cercanos usando Google Maps API.
        Si se especifica location, busca en esa ciudad. Si no, usa Barcelona por defecto.
        """
        try:
            self.logger.info(f"🔍 Iniciando búsqueda de centros médicos para especialidad '{specialty}'")
            google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")
            if not google_maps_key:
                self.logger.error("❌ Google Maps API key NO encontrada en variables de entorno")
                return {
                    "error": "Google Maps API key not found",
                    "message": "La API key de Google Maps no está configurada. Agrega GOOGLE_MAPS_API_KEY a tus variables de entorno."
                }
            
            # Verificar que la API key funcione haciendo una prueba
            test_result = self._test_google_maps_api(google_maps_key)
            if not test_result:
                return {
                    "error": "Google Maps API key invalid",
                    "message": "La API key de Google Maps no es válida o no tiene permisos. Verifica tu configuración."
                }

            # Si se especifica una ubicación, obtener sus coordenadas
            if location and location.lower() not in ["españa", "spain", "barcelona"]:
                self.logger.info(f"📍 Buscando coordenadas para '{location}'")
                coords = self._get_location_coordinates(location, google_maps_key)
                if coords:
                    lat, lng = coords
                    self.logger.info(f"📍 Usando coordenadas de '{location}': {lat}, {lng}")
                    return self._search_google_maps_nearby(lat, lng, specialty, google_maps_key)
                else:
                    self.logger.warning(f"⚠️ No se pudieron obtener coordenadas para '{location}', usando Barcelona por defecto")

            # Usar coordenadas por defecto (Barcelona centro)
            default_lat, default_lng = 41.3851, 2.1734  # Barcelona centro
            self.logger.info(f"📍 Usando coordenadas por defecto (Barcelona): {default_lat}, {default_lng}")

            # Buscar centros médicos cercanos usando nearbysearch
            return self._search_google_maps_nearby(default_lat, default_lng, specialty, google_maps_key)

        except Exception as e:
            self.logger.error(f"❌ Error en búsqueda de centros médicos: {e}")
            return {
                "error": f"Error en búsqueda: {str(e)}",
                "message": "No se pudo completar la búsqueda de centros médicos."
            }

    def _get_location_coordinates(self, location: str, api_key: str):
        """Obtiene las coordenadas (lat, lng) de una ciudad usando Geocoding API"""
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': location,
                'key': api_key,
                'region': 'es',
                'language': 'es'
            }
            response = self.session.get(url, params=params)
            data = response.json()
            if data.get('status') == 'OK' and data['results']:
                loc = data['results'][0]['geometry']['location']
                return loc['lat'], loc['lng']
            else:
                self.logger.warning(f"⚠️ No se encontraron coordenadas para '{location}' (status: {data.get('status')})")
                return None
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo coordenadas: {e}")
            return None

    def _search_google_maps_nearby(self, lat: float, lng: float, specialty: str, api_key: str) -> Dict[str, Any]:
        """Busca centros médicos cercanos usando nearbysearch y rankby=distance"""
        try:
            self.logger.info(f"🗺️ Realizando búsqueda nearbysearch para lat={lat}, lng={lng}, especialidad={specialty}")
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f'{lat},{lng}',
                'rankby': 'distance',
                'keyword': f'centro médico {specialty}',
                'key': api_key,
                'language': 'es',
                'type': 'health'
            }
            response = self.session.get(url, params=params)
            data = response.json()
            if data.get('status') == 'OK':
                places = data.get('results', [])
                self.logger.info(f"✅ Google Maps NearbySearch exitosa: {len(places)} lugares encontrados")
                for i, place in enumerate(places[:3]):
                    self.logger.info(f"📍 Resultado {i+1}: {place.get('name', 'N/A')} - {place.get('vicinity', 'N/A')}")
                centers = []
                for place in places[:5]:  # Top 5 resultados
                    place_id = place.get('place_id', '')
                    place_details = self._get_place_details(place_id, api_key) if place_id else {}
                    center_info = {
                        "name": place.get('name', ''),
                        "address": place.get('vicinity', ''),
                        "rating": place.get('rating', 0),
                        "phone": place_details.get('formatted_phone_number', ''),
                        "website": place_details.get('website', ''),
                        "google_maps_url": f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else "",
                        "types": place.get('types', []),
                        "opening_hours": place_details.get('opening_hours', {}),
                        "reviews_count": place.get('user_ratings_total', 0)
                    }
                    centers.append(center_info)
                return {
                    "source": "Google Maps NearbySearch",
                    "total_results": len(places),
                    "centers": centers
                }
            else:
                error_msg = f"Google Maps NearbySearch error: {data.get('status')}"
                self.logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
        except Exception as e:
            self.logger.error(f"❌ Error en Google Maps NearbySearch: {e}")
            raise
    
    def _get_place_details(self, place_id: str, api_key: str) -> Dict[str, Any]:
        """Obtiene información detallada de un lugar específico"""
        try:
            if not place_id:
                return {}
            
            url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                'place_id': place_id,
                'key': api_key,
                'language': 'es',
                'fields': 'formatted_phone_number,website,opening_hours'
            }
            
            response = self.session.get(url, params=params)
            data = response.json()
            
            if data.get('status') == 'OK':
                result = data.get('result', {})
                return {
                    'formatted_phone_number': result.get('formatted_phone_number', ''),
                    'website': result.get('website', ''),
                    'opening_hours': result.get('opening_hours', {})
                }
            else:
                self.logger.warning(f"⚠️ No se pudieron obtener detalles para place_id: {place_id}")
                return {}
                
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo detalles del lugar: {e}")
            return {}
    
    def _test_google_maps_api(self, api_key: str) -> bool:
        """Prueba si la API key de Google Maps funciona correctamente"""
        try:
            self.logger.info("🔍 Probando Google Maps API key...")
            
            # Hacer una petición simple a la API de Geocoding
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': 'Madrid',
                'key': api_key
            }
            
            response = self.session.get(url, params=params)
            data = response.json()
            
            if data.get('status') == 'OK':
                self.logger.info("✅ Google Maps API key funciona correctamente")
                return True
            elif data.get('status') == 'REQUEST_DENIED':
                self.logger.error(f"❌ Google Maps API key rechazada: {data.get('error_message', 'Sin mensaje de error')}")
                return False
            else:
                self.logger.error(f"❌ Google Maps API error: {data.get('status')}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error probando Google Maps API: {e}")
            return False
    
    
    


# Instancia global
web_search_provider = WebSearchProvider() 