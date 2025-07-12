"""
Script de prueba para el sistema RAG de audífonos.
Demuestra el funcionamiento completo del sistema.
"""

import asyncio
import logging
from agent.services.rag_service import RagService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_rag_system():
    """Prueba completa del sistema RAG."""
    
    print("🚀 Iniciando prueba del sistema RAG de audífonos...")
    
    # Inicializar RAG Service
    rag_service = RagService()
    
    # 1. Actualizar base de datos con web scraping
    print("\n📱 Paso 1: Actualizando base de datos con web scraping...")
    update_result = await rag_service.update_hearing_aids_database()
    
    if update_result['success']:
        print(f"✅ Base de datos actualizada: {update_result['audifonos_procesados']} audífonos")
    else:
        print(f"❌ Error actualizando base de datos: {update_result['message']}")
        return
    
    # 2. Mostrar estadísticas
    print("\n📊 Paso 2: Estadísticas de la base de datos...")
    stats = rag_service.get_database_stats()
    if 'error' not in stats:
        print(f"   Total audífonos: {stats['total_audifonos']}")
        print(f"   Marcas: {stats['marcas']}")
        print(f"   Tecnologías populares: {stats['tecnologias_populares']}")
    else:
        print(f"❌ Error obteniendo estadísticas: {stats['error']}")
    
    # 3. Probar búsquedas
    print("\n🔍 Paso 3: Probando búsquedas...")
    
    queries = [
        "audífonos con bluetooth",
        "audífonos recargables",
        "audífonos resistentes al agua",
        "audífonos pequeños y discretos",
        "audífonos con app para smartphone"
    ]
    
    for query in queries:
        print(f"\n   Buscando: '{query}'")
        results = rag_service.search_similar_hearing_aids(query, n_results=2)
        
        if results:
            for i, result in enumerate(results, 1):
                similarity = int(result['similarity_score'] * 100)
                print(f"     {i}. {result['modelo']} ({similarity}% similar)")
                print(f"        Marca: {result['marca']}")
                print(f"        Tecnologías: {result['tecnologias']}")
                print(f"        Conectividad: {result['conectividad']}")
        else:
            print("     No se encontraron resultados similares")
    
    print("\n✅ Prueba del sistema RAG completada!")


def test_embedding_providers():
    """Prueba los proveedores de embeddings."""
    
    print("\n🧠 Probando proveedores de embeddings...")
    
    from agent.providers.embeddings.embedding_manager import EmbeddingManager
    
    manager = EmbeddingManager.get_instance()
    
    # Verificar proveedores disponibles
    available_providers = manager.get_available_providers()
    print(f"   Proveedores disponibles: {available_providers}")
    
    # Probar generación de embeddings
    test_text = "audífono con bluetooth y recargable"
    
    for provider in available_providers:
        try:
            embedding = manager.get_embeddings(provider, test_text)
            dimension = manager.get_provider(provider).get_embedding_dimension()
            print(f"   ✅ {provider}: embedding generado ({dimension} dimensiones)")
        except Exception as e:
            print(f"   ❌ {provider}: error - {e}")


if __name__ == "__main__":
    # Probar proveedores de embeddings
    test_embedding_providers()
    
    # Probar sistema RAG completo
    asyncio.run(test_rag_system()) 