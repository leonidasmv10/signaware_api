"""
Script de debug para ver qué URLs se están obteniendo de Phonak.
"""

import asyncio
import logging
from agent.providers.hearing_aids_scraping.hearing_aids_scraper import PhonakScraper

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def debug_phonak_scraping():
    """Debug del scraping de Phonak."""
    
    print("🔍 Debug del scraping de Phonak...")
    
    scraper = PhonakScraper()
    
    # 1. Probar scraping de modelos básicos
    print("\n📱 Paso 1: Scraping de modelos básicos...")
    models = await scraper.scrape_models()
    
    print(f"\n📊 Resultados obtenidos: {len(models)} modelos")
    for i, model in enumerate(models, 1):
        print(f"\n{i}. {model['modelo']}")
        print(f"   URL: {model['url']}")
        print(f"   Marca: {model['marca']}")
    
    # 2. Probar scraping de detalles específicos
    if models:
        print(f"\n🔍 Paso 2: Probando detalles del primer modelo...")
        first_model = models[0]
        
        details = await scraper.scrape_model_details(first_model["url"])
        if details:
            print(f"✅ Detalles obtenidos para: {details['modelo']}")
            print(f"   URL: {details['url']}")
            print(f"   Tecnologías: {details['caracteristicas']['tecnologia']}")
            print(f"   Conectividad: {details['caracteristicas']['conectividad']}")
            print(f"   Batería: {details['caracteristicas']['bateria']}")
            print(f"   Resistencia agua: {details['caracteristicas']['resistencia_agua']}")
        else:
            print("❌ No se pudieron obtener detalles")
    
    # 3. Probar scraping de imágenes
    if models:
        print(f"\n🖼️ Paso 3: Probando imágenes del primer modelo...")
        first_model = models[0]
        
        images = await scraper.scrape_model_images(first_model["url"])
        if images:
            print(f"✅ Imágenes obtenidas: {len(images)} imágenes")
            for i, img_url in enumerate(images[:3], 1):
                print(f"   {i}. {img_url}")
        else:
            print("❌ No se pudieron obtener imágenes")


async def test_specific_url():
    """Probar una URL específica de Phonak."""
    
    print("\n🎯 Probando URL específica...")
    
    # URL específica de un modelo Phonak
    test_url = "https://www.phonak.com/es-es/dispositivos-auditivos/audifonos/virto-infinio"
    
    scraper = PhonakScraper()
    
    try:
        details = await scraper.scrape_model_details(test_url)
        if details:
            print(f"✅ URL específica funciona: {details['modelo']}")
            print(f"   URL: {details['url']}")
            print(f"   Características: {details['caracteristicas']}")
        else:
            print("❌ URL específica no funciona")
    except Exception as e:
        print(f"❌ Error con URL específica: {e}")


if __name__ == "__main__":
    # Debug del scraping general
    asyncio.run(debug_phonak_scraping())
    
    # Probar URL específica
    asyncio.run(test_specific_url()) 