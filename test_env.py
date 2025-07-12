#!/usr/bin/env python
"""
Script de prueba para verificar la carga de variables de entorno
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Verificar variables
google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")
news_key = os.getenv("NEWS_API_KEY")

print("🔍 Verificando variables de entorno...")
print(f"Google Maps API Key: {'✅ Configurada' if google_maps_key else '❌ No encontrada'}")
print(f"OpenAI API Key: {'✅ Configurada' if openai_key else '❌ No encontrada'}")
print(f"News API Key: {'✅ Configurada' if news_key else '❌ No encontrada'}")

if google_maps_key:
    print(f"Google Maps Key (primeros 10 chars): {google_maps_key[:10]}...")
else:
    print("❌ Google Maps API Key no está configurada") 