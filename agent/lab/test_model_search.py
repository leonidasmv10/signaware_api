"""
Script para probar la búsqueda específica por nombre de modelo de audífonos.
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.nodes.chatbot_nodes import ChatbotNodes
from agent.services.rag_service import RagService

async def test_model_search():
    """Prueba la búsqueda específica por nombre de modelo."""
    print("🧪 Iniciando prueba de búsqueda por nombre de modelo...")
    
    # Crear instancia de nodos
    nodes = ChatbotNodes()
    rag_service = RagService()
    
    # Casos de prueba específicos
    test_cases = [
        "Quiero información sobre el Virto Infinio",
        "Busco el modelo Naida Paradise",
        "Necesito detalles del Sky M",
        "¿Qué tal es el Audeo Paradise?",
        "Virto Infinio con bluetooth",
        "Naida Paradise recargable",
        "Audífonos Virto",
        "Modelo Sky"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"🔍 Prueba {i}: '{test_input}'")
        print(f"{'='*60}")
        
        try:
            # Buscar modelo específico
            specific_url = nodes._find_specific_model_url(test_input, rag_service)
            
            if specific_url:
                print(f"✅ Modelo específico encontrado:")
                print(f"   URL: {specific_url}")
                
                # Hacer scraping en tiempo real de esa URL específica
                print(f"🔄 Haciendo scraping en tiempo real...")
                results = await nodes._scrape_hearing_aids_realtime(test_input)
                
                if results:
                    print(f"✅ Scraping completado:")
                    for j, hearing_aid in enumerate(results, 1):
                        print(f"\n📱 Audífono {j}:")
                        print(f"   Modelo: {hearing_aid['modelo']}")
                        print(f"   URL: {hearing_aid['url']}")
                        print(f"   Similitud: {hearing_aid['similarity_score']:.2f}")
                        print(f"   Tecnologías: {hearing_aid['tecnologias']}")
                        print(f"   Conectividad: {hearing_aid['conectividad']}")
                        print(f"   Documento (primeros 300 chars): {hearing_aid['document'][:300]}...")
                else:
                    print("❌ No se pudo hacer scraping del modelo específico")
            else:
                print("❌ No se encontró un modelo específico para esta consulta")
                
        except Exception as e:
            print(f"❌ Error en prueba {i}: {e}")
    
    print(f"\n{'='*60}")
    print("🏁 Prueba de búsqueda por nombre de modelo completada")
    print(f"{'='*60}")

async def test_full_node_with_specific_model():
    """Prueba el nodo completo con consultas específicas de modelos."""
    print("\n🧪 Iniciando prueba del nodo completo con modelos específicos...")
    
    # Crear instancia de nodos
    nodes = ChatbotNodes()
    
    # Casos de prueba específicos
    test_cases = [
        "Quiero información sobre el Virto Infinio",
        "Busco el modelo Naida Paradise con bluetooth",
        "¿Qué características tiene el Sky M?"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"🔍 Prueba nodo completo {i}: '{test_input}'")
        print(f"{'='*60}")
        
        # Estado de prueba
        test_state = {
            "user_input": test_input,
            "text_generator_model": "gemini"
        }
        
        try:
            # Ejecutar el nodo completo
            final_state = await nodes._hearing_aids_node_async(test_state)
            
            print(f"✅ Nodo ejecutado exitosamente")
            print(f"📝 Respuesta generada:")
            print(f"{'='*50}")
            print(final_state.get("response", "Sin respuesta"))
            print(f"{'='*50}")
            
        except Exception as e:
            print(f"❌ Error en nodo completo: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de búsqueda por nombre de modelo...")
    
    # Ejecutar pruebas
    asyncio.run(test_model_search())
    asyncio.run(test_full_node_with_specific_model())
    
    print("\n✅ Todas las pruebas completadas") 