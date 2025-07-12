"""
Servicio RAG (Retrieval-Augmented Generation) para audífonos.
Integra web scraping en tiempo real, embeddings y ChromaDB.
"""

import asyncio
import logging
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
from ..providers.embeddings.embedding_manager import EmbeddingManager


class RagService:
    """Servicio RAG para audífonos con web scraping en tiempo real."""
    
    def __init__(self):
        """Inicializa el servicio RAG."""
        self.logger = logging.getLogger(__name__)
        self.embedding_manager = EmbeddingManager.get_instance()
        
        # Inicializar ChromaDB
        try:
            self.client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name="hearing_aids",
                metadata={"description": "Base de datos vectorial de audífonos"}
            )
            self.logger.info("✅ ChromaDB inicializado correctamente")
        except Exception as e:
            self.logger.error(f"❌ Error inicializando ChromaDB: {e}")
            self.client = None
            self.collection = None
    
    async def scrape_hearing_aids_data(self, brand: str = "phonak") -> List[Dict[str, Any]]:
        """
        Realiza web scraping de audífonos en tiempo real.
        
        Args:
            brand: Marca de audífonos a scrapear (phonak, etc.)
            
        Returns:
            Lista de datos de audífonos
        """
        try:
            from ..providers.hearing_aids_scraping.hearing_aids_scraper import HearingAidsScrapingProvider
            
            # Usar el proveedor específico de scraping de audífonos
            scraping_provider = HearingAidsScrapingProvider()
            return await scraping_provider.scrape_brand(brand)
                
        except Exception as e:
            self.logger.error(f"Error en web scraping: {e}")
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
    
    def store_in_vector_db(self, datos: List[Dict[str, Any]]) -> bool:
        """
        Almacena los datos en ChromaDB con embeddings.
        
        Args:
            datos: Lista de datos de audífonos
            
        Returns:
            bool: True si se almacenó correctamente
        """
        if not self.collection:
            self.logger.error("❌ ChromaDB no disponible")
            return False
        
        try:
            # Preparar datos para ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            for i, dato in enumerate(datos):
                # Crear documento combinado
                doc_content = f"""
                Modelo: {dato['modelo']}
                Marca: {dato['marca']}
                URL: {dato['url']}
                
                Características:
                - Tecnologías: {', '.join(dato['caracteristicas']['tecnologia'])}
                - Conectividad: {', '.join(dato['caracteristicas']['conectividad'])}
                - Batería: {dato['caracteristicas']['bateria']} horas
                - Resistencia al agua: {dato['caracteristicas']['resistencia_agua']}
                
                Descripción: {dato['texto_completo'][:1000]}...
                """
                
                documents.append(doc_content)
                metadatas.append({
                    "modelo": dato['modelo'],
                    "marca": dato['marca'],
                    "url": dato['url'],
                    "fecha_scraping": dato['fecha_scraping'],
                    "tecnologias": ', '.join(dato['caracteristicas']['tecnologia']),
                    "conectividad": ', '.join(dato['caracteristicas']['conectividad'])
                })
                ids.append(f"hearing_aid_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Generar embeddings
            embeddings = []
            for doc in documents:
                try:
                    embedding = self.embedding_manager.get_embeddings("openai", doc)
                    embeddings.append(embedding)
                except Exception as e:
                    self.logger.error(f"Error generando embedding: {e}")
                    # Usar embedding de fallback
                    embedding = self.embedding_manager.get_embeddings("huggingface", doc)
                    embeddings.append(embedding)
            
            # Almacenar en ChromaDB
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            self.logger.info(f"✅ {len(datos)} audífonos almacenados en ChromaDB")
            return True
            
        except Exception as e:
            self.logger.error(f"Error almacenando en ChromaDB: {e}")
            return False
    
    def search_similar_hearing_aids(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Busca audífonos similares usando embeddings.
        
        Args:
            query: Consulta del usuario
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de audífonos similares
        """
        if not self.collection:
            self.logger.error("❌ ChromaDB no disponible")
            return []
        
        try:
            # Generar embedding de la consulta
            query_embedding = self.embedding_manager.get_embeddings("openai", query)
            
            # Buscar en ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Formatear resultados
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "modelo": results['metadatas'][0][i]['modelo'],
                    "marca": results['metadatas'][0][i]['marca'],
                    "url": results['metadatas'][0][i]['url'],
                    "tecnologias": results['metadatas'][0][i]['tecnologias'],
                    "conectividad": results['metadatas'][0][i]['conectividad'],
                    "similarity_score": 1 - results['distances'][0][i],  # Convertir distancia a similitud
                    "document": results['documents'][0][i]
                })
            
            self.logger.info(f"🔍 Encontrados {len(formatted_results)} audífonos similares")
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error buscando audífonos: {e}")
            return []
    
    async def update_hearing_aids_database(self) -> Dict[str, Any]:
        """
        Actualiza la base de datos de audífonos con scraping en tiempo real.
        
        Returns:
            Dict con el resultado de la actualización
        """
        try:
            self.logger.info("🔄 Iniciando actualización de base de datos de audífonos...")
            
            # Realizar scraping
            datos = await self.scrape_hearing_aids_data("phonak")
            
            if not datos:
                return {
                    "success": False,
                    "message": "No se pudieron obtener datos de audífonos",
                    "audifonos_procesados": 0
                }
            
            # Almacenar en vector DB
            stored = self.store_in_vector_db(datos)
            
            if stored:
                return {
                    "success": True,
                    "message": "Base de datos actualizada correctamente",
                    "audifonos_procesados": len(datos),
                    "fecha_actualizacion": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": "Error almacenando en base de datos vectorial",
                    "audifonos_procesados": len(datos)
                }
                
        except Exception as e:
            self.logger.error(f"Error actualizando base de datos: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "audifonos_procesados": 0
            }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la base de datos vectorial.
        
        Returns:
            Dict con estadísticas de la base de datos
        """
        if not self.collection:
            return {"error": "ChromaDB no disponible"}
        
        try:
            count = self.collection.count()
            
            # Obtener metadatos para análisis
            results = self.collection.get(include=["metadatas"])
            
            # Analizar marcas
            marcas = {}
            tecnologias = {}
            
            for metadata in results['metadatas']:
                marca = metadata.get('marca', 'Desconocida')
                marcas[marca] = marcas.get(marca, 0) + 1
                
                # Analizar tecnologías
                techs = metadata.get('tecnologias', '').split(', ')
                for tech in techs:
                    if tech.strip():
                        tecnologias[tech.strip()] = tecnologias.get(tech.strip(), 0) + 1
            
            return {
                "total_audifonos": count,
                "marcas": marcas,
                "tecnologias_populares": dict(sorted(tecnologias.items(), 
                                                    key=lambda x: x[1], reverse=True)[:5]),
                "ultima_actualizacion": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)}
    
    def get_all_hearing_aid_urls(self) -> List[str]:
        """
        Obtiene todas las URLs de audífonos almacenadas en la base de datos RAG.
        
        Returns:
            Lista de URLs únicas de audífonos
        """
        if not self.collection:
            self.logger.error("❌ ChromaDB no disponible")
            return []
        
        try:
            # Obtener todos los metadatos
            results = self.collection.get(include=["metadatas"])
            
            # Extraer URLs únicas
            urls = set()
            for metadata in results['metadatas']:
                url = metadata.get('url')
                if url and url not in urls:
                    urls.add(url)
            
            self.logger.info(f"✅ Obtenidas {len(urls)} URLs únicas de audífonos desde RAG")
            return list(urls)
            
        except Exception as e:
            self.logger.error(f"Error obteniendo URLs: {e}")
            return [] 