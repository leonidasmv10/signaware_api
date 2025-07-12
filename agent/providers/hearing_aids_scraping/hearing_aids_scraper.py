"""
Proveedor de web scraping específico para audífonos.
Integra los scrapers existentes de Phonak y otros fabricantes.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod
import re


class HearingAidsScraper(ABC):
    """Clase base abstracta para scrapers de audífonos."""
    
    def __init__(self):
        """Inicializa el scraper."""
        self.logger = logging.getLogger(__name__)
    
    @abstractmethod
    async def scrape_models(self) -> List[Dict[str, Any]]:
        """
        Scrapea los modelos de audífonos disponibles.
        
        Returns:
            Lista de modelos con información básica
        """
        pass
    
    @abstractmethod
    async def scrape_model_details(self, model_url: str) -> Dict[str, Any]:
        """
        Scrapea detalles específicos de un modelo.
        
        Args:
            model_url: URL del modelo específico
            
        Returns:
            Diccionario con detalles del modelo
        """
        pass
    
    @abstractmethod
    async def scrape_model_images(self, model_url: str) -> List[str]:
        """
        Scrapea imágenes de un modelo específico.
        
        Args:
            model_url: URL del modelo específico
            
        Returns:
            Lista de URLs de imágenes
        """
        pass


class PhonakScraper(HearingAidsScraper):
    """Scraper específico para audífonos Phonak."""
    
    def __init__(self):
        """Inicializa el scraper de Phonak."""
        super().__init__()
        self.base_url = "https://www.phonak.com"
        self.models_url = f"{self.base_url}/es-es/dispositivos-auditivos/audifonos"
    
    async def scrape_models(self) -> List[Dict[str, Any]]:
        """
        Scrapea todos los modelos de audífonos Phonak.
        
        Returns:
            Lista de modelos con información básica
        """
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Navegar a la página principal
                await page.goto(self.models_url, timeout=60000)
                
                # Esperar a que carguen los enlaces
                await page.wait_for_selector(
                    "a[href*='/es-es/dispositivos-auditivos/audifonos/']", 
                    state="attached", 
                    timeout=30000
                )
                
                # Obtener todos los enlaces de audífonos específicos
                enlaces = await page.query_selector_all(
                    "a[href*='/es-es/dispositivos-auditivos/audifonos/']"
                )
                urls = []
                for enlace in enlaces:
                    href = await enlace.get_attribute("href")
                    if href and href.startswith("/es-es/dispositivos-auditivos/audifonos/"):
                        # Verificar que no sea una página genérica
                        if not any(generic in href.lower() for generic in ["guia", "comparar", "todos", "categoria"]):
                            urls.append(href)
                
                # Eliminar duplicados manteniendo el orden
                urls = list(dict.fromkeys(urls))
                
                self.logger.info(f"🔍 Encontrados {len(urls)} modelos de audífonos Phonak")
                
                models = []
                for i, path in enumerate(urls, 1):
                    url = f"{self.base_url}{path}"
                    self.logger.info(f"📱 Procesando {i}/{len(urls)}: {url}")
                    
                    try:
                        await page.goto(url, timeout=30000)
                        await page.wait_for_selector("h1", timeout=10000)
                        
                        # Extraer información básica
                        nombre = await (await page.query_selector("h1")).inner_text()
                        
                        # Verificar que el nombre sea específico de un modelo
                        if nombre and len(nombre.strip()) > 3 and not any(generic in nombre.lower() for generic in ["guia", "comparar", "todos", "categoria", "audifonos"]):
                            models.append({
                                "modelo": nombre.strip(),
                                "url": url,
                                "marca": "Phonak",
                                "fecha_scraping": datetime.now().isoformat()
                            })
                            self.logger.info(f"✅ Modelo válido encontrado: {nombre}")
                        else:
                            self.logger.warning(f"⚠️ Modelo genérico descartado: {nombre}")
                        
                    except Exception as e:
                        self.logger.error(f"Error procesando {url}: {e}")
                        continue
                
                await browser.close()
                self.logger.info(f"✅ Scraping de modelos completado: {len(models)} modelos")
                return models
                
        except Exception as e:
            self.logger.error(f"Error en scraping de modelos Phonak: {e}")
            return []
    
    async def scrape_model_details(self, model_url: str) -> Dict[str, Any]:
        """
        Scrapea detalles específicos de un modelo Phonak.
        
        Args:
            model_url: URL del modelo específico
            
        Returns:
            Diccionario con detalles del modelo
        """
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(model_url, timeout=30000)
                
                # Esperar a que cargue el contenido
                await asyncio.sleep(3)
                
                # Extraer texto completo de la página
                texto_completo = await page.evaluate("""
                    () => {
                        function esVisible(elemento) {
                            const estilo = window.getComputedStyle(elemento);
                            return estilo &&
                                   estilo.visibility !== 'hidden' &&
                                   estilo.display !== 'none' &&
                                   elemento.offsetHeight > 0 &&
                                   elemento.offsetWidth > 0;
                        }
                        
                        const excluir = ['HEADER', 'NAV', 'FOOTER', 'SCRIPT', 'STYLE'];
                        const texto = new Set();
                        const nodos = document.body.querySelectorAll('*');
                        
                        nodos.forEach(nodo => {
                            if (esVisible(nodo) && !excluir.includes(nodo.tagName) && 
                                !nodo.closest('header, nav, footer')) {
                                const contenido = nodo.innerText || nodo.textContent;
                                if (contenido) {
                                    const limpio = contenido.trim();
                                    if (limpio.length > 20) {
                                        texto.add(limpio);
                                    }
                                }
                            }
                        });
                        
                        return Array.from(texto).join('\\n\\n');
                    }
                """)
                
                # Extraer características específicas
                caracteristicas = self._extract_features(texto_completo)
                
                # Obtener nombre del modelo
                nombre = await (await page.query_selector("h1")).inner_text()
                
                await browser.close()
                
                return {
                    "modelo": nombre,
                    "url": model_url,
                    "texto_completo": texto_completo,
                    "caracteristicas": caracteristicas,
                    "marca": "Phonak",
                    "fecha_scraping": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error scraping detalles de {model_url}: {e}")
            return {}
    
    async def scrape_model_images(self, model_url: str) -> List[str]:
        """
        Scrapea imágenes de un modelo específico.
        
        Args:
            model_url: URL del modelo específico
            
        Returns:
            Lista de URLs de imágenes
        """
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(model_url, timeout=30000)
                
                # Esperar a que cargue el contenido
                await asyncio.sleep(3)
                
                # Extraer URLs de imágenes visibles
                imagenes = await page.evaluate("""
                    () => {
                        function esVisible(elemento) {
                            const style = window.getComputedStyle(elemento);
                            return style && style.visibility !== 'hidden' && 
                                   style.display !== 'none' && elemento.offsetHeight > 0 && 
                                   elemento.offsetWidth > 0;
                        }
                        const imgs = Array.from(document.images);
                        return imgs.filter(img => esVisible(img)).map(img => img.src);
                    }
                """)
                
                await browser.close()
                return imagenes[:5]  # Limitar a 5 imágenes
                
        except Exception as e:
            self.logger.error(f"Error scraping imágenes de {model_url}: {e}")
            return []
    
    def _extract_features(self, texto: str) -> Dict[str, Any]:
        """Extrae características específicas del texto."""
        caracteristicas = {
            "tecnologia": [],
            "conectividad": [],
            "bateria": None,
            "resistencia_agua": None,
            "tamaño": None,
            "precio_estimado": None
        }
        
        # Patrones para extraer características
        patterns = {
            "tecnologia": [
                r"bluetooth", r"wifi", r"wireless", r"smart", r"digital", r"analógico",
                r"rechargeable", r"recargable", r"waterproof", r"resistente.*agua"
            ],
            "conectividad": [
                r"bluetooth", r"wifi", r"wireless", r"app", r"smartphone", r"móvil"
            ],
            "bateria": [
                r"(\d+)\s*(?:horas?|h)\s*batería", r"batería\s*(\d+)\s*(?:horas?|h)",
                r"(\d+)\s*días?\s*batería"
            ],
            "resistencia_agua": [
                r"IP(\d+)", r"resistente.*agua", r"waterproof", r"impermeable"
            ],
            "tamaño": [
                r"(\d+(?:\.\d+)?)\s*(?:mm|cm)", r"pequeño", r"grande", r"discreto"
            ]
        }
        
        texto_lower = texto.lower()
        
        # Extraer tecnologías
        for pattern in patterns["tecnologia"]:
            if re.search(pattern, texto_lower):
                caracteristicas["tecnologia"].append(re.search(pattern, texto_lower).group())
        
        # Extraer conectividad
        for pattern in patterns["conectividad"]:
            if re.search(pattern, texto_lower):
                caracteristicas["conectividad"].append(re.search(pattern, texto_lower).group())
        
        # Extraer batería
        for pattern in patterns["bateria"]:
            match = re.search(pattern, texto_lower)
            if match:
                caracteristicas["bateria"] = match.group(1)
                break
        
        # Extraer resistencia al agua
        for pattern in patterns["resistencia_agua"]:
            match = re.search(pattern, texto_lower)
            if match:
                caracteristicas["resistencia_agua"] = match.group(1) if match.groups() else True
                break
        
        return caracteristicas


class HearingAidsScrapingProvider:
    """Proveedor principal para scraping de audífonos."""
    
    def __init__(self):
        """Inicializa el proveedor de scraping."""
        self.logger = logging.getLogger(__name__)
        self.scrapers = {
            "phonak": PhonakScraper()
        }
    
    async def scrape_brand(self, brand: str) -> List[Dict[str, Any]]:
        """
        Scrapea audífonos de una marca específica.
        
        Args:
            brand: Marca de audífonos (phonak, etc.)
            
        Returns:
            Lista de audífonos con información completa
        """
        if brand.lower() not in self.scrapers:
            self.logger.error(f"Marca {brand} no soportada")
            return []
        
        scraper = self.scrapers[brand.lower()]
        
        try:
            # Obtener modelos básicos
            models = await scraper.scrape_models()
            
            # Obtener detalles completos para cada modelo
            detailed_models = []
            for model in models:
                try:
                    # Obtener detalles
                    details = await scraper.scrape_model_details(model["url"])
                    if details:
                        # Obtener imágenes
                        images = await scraper.scrape_model_images(model["url"])
                        details["imagenes"] = images
                        detailed_models.append(details)
                        
                except Exception as e:
                    self.logger.error(f"Error procesando {model['url']}: {e}")
                    continue
            
            self.logger.info(f"✅ Scraping completado para {brand}: {len(detailed_models)} modelos")
            return detailed_models
            
        except Exception as e:
            self.logger.error(f"Error en scraping de {brand}: {e}")
            return []
    
    async def scrape_all_brands(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scrapea todas las marcas disponibles.
        
        Returns:
            Diccionario con audífonos por marca
        """
        results = {}
        
        for brand in self.scrapers.keys():
            self.logger.info(f"🔄 Scraping {brand}...")
            results[brand] = await self.scrape_brand(brand)
        
        return results 