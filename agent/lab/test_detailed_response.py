"""
Script para probar que el sistema genera respuestas detalladas con información del scraping en tiempo real.
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.nodes.chatbot_nodes import ChatbotNodes

async def test_detailed_response():
    """Prueba que el sistema genera respuestas detalladas."""
    print("🧪 Probando generación de respuestas detalladas...")
    
    # Crear instancia de nodos
    nodes = ChatbotNodes()
    
    # Casos de prueba específicos
    test_cases = [
        "Quiero información detallada sobre el Virto Infinio",
        "¿Qué características tiene el Naida Paradise?",
        "Necesito detalles técnicos del Sky M",
        "Cuéntame todo sobre el Audeo Paradise"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"🔍 Prueba {i}: '{test_input}'")
        print(f"{'='*70}")
        
        try:
            # Estado de prueba
            test_state = {
                "user_input": test_input,
                "text_generator_model": "gemini"
            }
            
            # Ejecutar el nodo completo
            final_state = await nodes._hearing_aids_node_async(test_state)
            
            print(f"✅ Nodo ejecutado exitosamente")
            print(f"📝 Respuesta generada:")
            print(f"{'='*50}")
            print(final_state.get("response", "Sin respuesta"))
            print(f"{'='*50}")
            
            # Verificar si la respuesta es detallada
            response = final_state.get("response", "")
            if len(response) > 200:
                print(f"✅ Respuesta detallada: {len(response)} caracteres")
            else:
                print(f"⚠️ Respuesta muy corta: {len(response)} caracteres")
            
        except Exception as e:
            print(f"❌ Error en prueba {i}: {e}")
    
    print(f"\n{'='*70}")
    print("🏁 Prueba de respuestas detalladas completada")
    print(f"{'='*70}")

async def test_scraping_content():
    """Prueba específicamente el contenido del scraping."""
    print("\n🧪 Probando contenido del scraping...")
    
    # Crear instancia de nodos
    nodes = ChatbotNodes()
    
    try:
        # Probar scraping en tiempo real
        results = await nodes._scrape_hearing_aids_realtime("Virto Infinio")
        
        if results:
            print(f"✅ Scraping completado: {len(results)} audífonos")
            
            for i, hearing_aid in enumerate(results, 1):
                print(f"\n📱 Audífono {i}:")
                print(f"   Modelo: {hearing_aid['modelo']}")
                print(f"   URL: {hearing_aid['url']}")
                print(f"   Similitud: {hearing_aid['similarity_score']:.2f}")
                print(f"   Tecnologías: {hearing_aid['tecnologias']}")
                print(f"   Conectividad: {hearing_aid['conectividad']}")
                print(f"   Documento (primeros 300 chars): {hearing_aid['document'][:300]}...")
                
                # Verificar si hay información detallada
                if len(hearing_aid['document']) > 100:
                    print(f"   ✅ Documento detallado: {len(hearing_aid['document'])} caracteres")
                else:
                    print(f"   ⚠️ Documento muy corto: {len(hearing_aid['document'])} caracteres")
        else:
            print("❌ No se obtuvieron resultados del scraping")
            
    except Exception as e:
        print(f"❌ Error en scraping: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de respuestas detalladas...")
    
    # Ejecutar pruebas
    asyncio.run(test_detailed_response())
    asyncio.run(test_scraping_content())
    
    print("\n✅ Todas las pruebas completadas") 