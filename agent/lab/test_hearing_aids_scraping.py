"""
Script de prueba para el sistema de scraping de audífonos.
Demuestra el funcionamiento del nuevo proveedor específico.
"""

import asyncio
import logging
from agent.providers.hearing_aids_scraping.hearing_aids_scraper import HearingAidsScrapingProvider

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_hearing_aids_scraping():
    """Prueba completa del sistema de scraping de audífonos."""
    
    print("🎧 Iniciando prueba del sistema de scraping de audífonos...")
    
    # Inicializar proveedor de scraping
    scraping_provider = HearingAidsScrapingProvider()
    
    # 1. Probar scraping de Phonak
    print("\n📱 Paso 1: Scraping de audífonos Phonak...")
    phonak_models = await scraping_provider.scrape_brand("phonak")
    
    if phonak_models:
        print(f"✅ Scraping Phonak completado: {len(phonak_models)} modelos")
        
        # Mostrar información de los primeros 3 modelos
        for i, model in enumerate(phonak_models[:3], 1):
            print(f"\n   {i}. {model['modelo']}")
            print(f"      URL: {model['url']}")
            print(f"      Marca: {model['marca']}")
            print(f"      Tecnologías: {', '.join(model['caracteristicas']['tecnologia'])}")
            print(f"      Conectividad: {', '.join(model['caracteristicas']['conectividad'])}")
            print(f"      Batería: {model['caracteristicas']['bateria']} horas")
            print(f"      Imágenes: {len(model['imagenes'])} encontradas")
    else:
        print("❌ No se pudieron obtener modelos de Phonak")
    
    # 2. Probar scraping de todas las marcas
    print("\n🔄 Paso 2: Scraping de todas las marcas disponibles...")
    all_brands = await scraping_provider.scrape_all_brands()
    
    for brand, models in all_brands.items():
        print(f"   {brand.capitalize()}: {len(models)} modelos")
    
    # 3. Probar scraping de detalles específicos
    if phonak_models:
        print("\n🔍 Paso 3: Probando scraping de detalles específicos...")
        first_model = phonak_models[0]
        
        # Obtener scraper específico
        phonak_scraper = scraping_provider.scrapers["phonak"]
        
        # Scrapear detalles
        details = await phonak_scraper.scrape_model_details(first_model["url"])
        if details:
            print(f"   ✅ Detalles obtenidos para: {details['modelo']}")
            print(f"      Características: {details['caracteristicas']}")
        
        # Scrapear imágenes
        images = await phonak_scraper.scrape_model_images(first_model["url"])
        if images:
            print(f"   ✅ Imágenes obtenidas: {len(images)} imágenes")
            for i, img_url in enumerate(images[:3], 1):
                print(f"      {i}. {img_url}")
    
    print("\n✅ Prueba del sistema de scraping completada!")


def test_scraper_classes():
    """Prueba las clases de scraper individuales."""
    
    print("\n🧪 Probando clases de scraper...")
    
    from agent.providers.hearing_aids_scraping.hearing_aids_scraper import PhonakScraper
    
    # Probar inicialización
    try:
        phonak_scraper = PhonakScraper()
        print("   ✅ PhonakScraper inicializado correctamente")
        print(f"      Base URL: {phonak_scraper.base_url}")
        print(f"      Models URL: {phonak_scraper.models_url}")
    except Exception as e:
        print(f"   ❌ Error inicializando PhonakScraper: {e}")
    
    # Probar extracción de características
    test_text = """
    El Virto B-Titanium es un audífono recargable con bluetooth y wifi.
    Tiene una batería de 24 horas y es resistente al agua IP68.
    Incluye conectividad con smartphone y app móvil.
    """
    
    try:
        features = phonak_scraper._extract_features(test_text)
        print("   ✅ Extracción de características funcionando")
        print(f"      Tecnologías: {features['tecnologia']}")
        print(f"      Conectividad: {features['conectividad']}")
        print(f"      Batería: {features['bateria']} horas")
        print(f"      Resistencia agua: {features['resistencia_agua']}")
    except Exception as e:
        print(f"   ❌ Error en extracción de características: {e}")


if __name__ == "__main__":
    # Probar clases de scraper
    test_scraper_classes()
    
    # Probar sistema completo
    asyncio.run(test_hearing_aids_scraping()) 