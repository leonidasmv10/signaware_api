"""
Script para verificar las URLs almacenadas en la base de datos RAG.
"""

import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.services.rag_service import RagService

def check_rag_urls():
    """Verifica las URLs almacenadas en la base de datos RAG."""
    print("🔍 Verificando URLs en la base de datos RAG...")
    
    try:
        # Crear instancia del servicio RAG
        rag_service = RagService()
        
        # Obtener estadísticas de la base de datos
        stats = rag_service.get_database_stats()
        print(f"\n📊 Estadísticas de la base de datos:")
        print(f"   Total de audífonos: {stats.get('total_audifonos', 0)}")
        print(f"   Marcas: {stats.get('marcas', {})}")
        print(f"   Tecnologías populares: {stats.get('tecnologias_populares', {})}")
        
        # Obtener todas las URLs
        urls = rag_service.get_all_hearing_aid_urls()
        print(f"\n🔗 URLs almacenadas en RAG ({len(urls)}):")
        
        if urls:
            for i, url in enumerate(urls, 1):
                print(f"   {i}. {url}")
        else:
            print("   ❌ No hay URLs almacenadas en RAG")
            print("   💡 Ejecuta el comando 'update_hearing_aids_db' para poblar la base de datos")
        
        # Verificar si las URLs son específicas de modelos
        if urls:
            print(f"\n🔍 Análisis de URLs:")
            generic_urls = []
            specific_urls = []
            
            for url in urls:
                if any(generic in url.lower() for generic in ['guia', 'guide', 'comparison', 'comparar', 'ayuda', 'help']):
                    generic_urls.append(url)
                else:
                    specific_urls.append(url)
            
            print(f"   URLs específicas de modelos: {len(specific_urls)}")
            print(f"   URLs genéricas: {len(generic_urls)}")
            
            if generic_urls:
                print(f"\n⚠️ URLs genéricas encontradas:")
                for url in generic_urls:
                    print(f"   - {url}")
        
    except Exception as e:
        print(f"❌ Error verificando URLs: {e}")

if __name__ == "__main__":
    check_rag_urls() 