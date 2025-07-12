"""
Script de prueba para el scraping en tiempo real de audífonos Phonak.
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.nodes.chatbot_nodes import ChatbotNodes

async def test_realtime_scraping():
    """Prueba el scraping en tiempo real de audífonos."""
    print("🧪 Iniciando prueba de scraping en tiempo real...")
    
    # Crear instancia de nodos
    nodes = ChatbotNodes()
    
    # Probar obtención de URLs desde RAG
    print("\n🔍 Probando obtención de URLs desde RAG...")
    try:
        from agent.services.rag_service import RagService
        rag_service = RagService()
        rag_urls = rag_service.get_all_hearing_aid_urls()
        print(f"✅ URLs obtenidas desde RAG: {len(rag_urls)}")
        for i, url in enumerate(rag_urls[:3], 1):  # Mostrar solo las primeras 3
            print(f"   {i}. {url}")
        if len(rag_urls) > 3:
            print(f"   ... y {len(rag_urls) - 3} más")
    except Exception as e:
        print(f"❌ Error obteniendo URLs desde RAG: {e}")
    
    # Casos de prueba
    test_cases = [
        "Quiero un audífono con bluetooth",
        "Busco audífonos Phonak Virto",
        "Necesito audífonos recargables",
        "Audífonos para niños",
        "Audífonos modernos con app"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"🔍 Prueba {i}: '{test_input}'")
        print(f"{'='*50}")
        
        try:
            # Ejecutar scraping en tiempo real
            results = await nodes._scrape_hearing_aids_realtime(test_input)
            
            if results:
                print(f"✅ Encontrados {len(results)} audífonos relevantes:")
                for j, hearing_aid in enumerate(results, 1):
                    print(f"\n📱 Audífono {j}:")
                    print(f"   Modelo: {hearing_aid['modelo']}")
                    print(f"   Marca: {hearing_aid['marca']}")
                    print(f"   URL: {hearing_aid['url']}")
                    print(f"   Similitud: {hearing_aid['similarity_score']:.2f}")
                    print(f"   Tecnologías: {hearing_aid['tecnologias']}")
                    print(f"   Conectividad: {hearing_aid['conectividad']}")
                    print(f"   Documento (primeros 200 chars): {hearing_aid['document'][:200]}...")
            else:
                print("❌ No se encontraron audífonos relevantes")
                
        except Exception as e:
            print(f"❌ Error en prueba {i}: {e}")
    
    print(f"\n{'='*50}")
    print("🏁 Prueba de scraping en tiempo real completada")
    print(f"{'='*50}")

async def test_full_node():
    """Prueba el nodo completo de audífonos."""
    print("\n🧪 Iniciando prueba del nodo completo...")
    
    # Crear instancia de nodos
    nodes = ChatbotNodes()
    
    # Estado de prueba
    test_state = {
        "user_input": "Quiero un audífono Phonak con bluetooth",
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
    print("🚀 Iniciando pruebas de scraping en tiempo real...")
    
    # Ejecutar pruebas
    asyncio.run(test_realtime_scraping())
    asyncio.run(test_full_node())
    
    print("\n✅ Todas las pruebas completadas") 