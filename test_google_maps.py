#!/usr/bin/env python
"""
Script para probar directamente la API de Google Maps
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_google_maps_search(location: str, specialty: str = "audífonos"):
    """Prueba la búsqueda de Google Maps API"""
    
    google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not google_maps_key:
        print("❌ Google Maps API key no encontrada")
        return
    
    # Construir query
    if location.lower() in ["españa", "spain"]:
        query = f"centros médicos {specialty}"
    else:
        query = f"centros médicos {specialty} en {location}"
    
    print(f"🔍 Probando: '{query}'")
    
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        'query': query,
        'key': google_maps_key,
        'language': 'es',
        'type': 'health',
        'region': 'es'
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('status') == 'OK':
            places = data.get('results', [])
            print(f"✅ Encontrados {len(places)} lugares")
            
            for i, place in enumerate(places[:5]):
                name = place.get('name', 'N/A')
                address = place.get('formatted_address', 'N/A')
                print(f"📍 {i+1}. {name}")
                print(f"   📍 {address}")
                print()
        else:
            print(f"❌ Error: {data.get('status')}")
            print(f"📝 Mensaje: {data.get('error_message', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")

# Probar diferentes ubicaciones
test_locations = [
    "Valencia",
    "Madrid", 
    "Barcelona",
    "Sevilla",
    "Bilbao"
]

print("🧪 Probando Google Maps API con diferentes ubicaciones...\n")

for location in test_locations:
    print(f"🏙️ Probando: {location}")
    print("=" * 50)
    test_google_maps_search(location)
    print() 