#!/usr/bin/env python
"""
Script para probar la extracción de ubicación en consultas médicas
"""

import re

def test_location_extraction(user_input: str):
    """Prueba la extracción de ubicación con el mismo algoritmo del chatbot"""
    
    # Ubicación por defecto
    location = "España"
    
    # Detectar ubicación - patrones mejorados
    location_patterns = [
        r"en\s+([A-Za-zÀ-ÿ\s]+?)(?:\s+centros?|\s+especialistas?|\s+clínicas?|\s+hospitales?|\s+centro)",
        r"busca\s+(?:centros?|especialistas?|clínicas?|hospitales?)\s+en\s+([A-Za-zÀ-ÿ\s]+)",
        r"centros?\s+en\s+([A-Za-zÀ-ÿ\s]+)",
        r"especialistas?\s+en\s+([A-Za-zÀ-ÿ\s]+)",
        r"clínicas?\s+en\s+([A-Za-zÀ-ÿ\s]+)",
        r"hospitales?\s+en\s+([A-Za-zÀ-ÿ\s]+)",
        r"([A-Za-zÀ-ÿ\s]+?)\s+centros?",
        r"([A-Za-zÀ-ÿ\s]+?)\s+especialistas?",
        r"([A-Za-zÀ-ÿ\s]+?)\s+hospitales?",
        r"([A-Za-zÀ-ÿ\s]+?)\s+clínicas?"
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            print(f"✅ Patrón '{pattern}' detectó: '{location}'")
            return location
    
    print(f"❌ No se detectó ubicación, usando por defecto: '{location}'")
    return location

# Probar diferentes inputs
test_inputs = [
    "busca centro en Valencia",
    "centros médicos en Madrid",
    "especialistas en Barcelona",
    "clínicas en Sevilla",
    "hospitales en Bilbao",
    "busca otorrinos en Valencia",
    "centros de audífonos en Valencia",
    "Valencia centros médicos",
    "Quiero encontrar centros en Valencia"
]

print("🧪 Probando extracción de ubicación...\n")

for i, test_input in enumerate(test_inputs, 1):
    print(f"Test {i}: '{test_input}'")
    location = test_location_extraction(test_input)
    print(f"📍 Resultado: '{location}'\n") 