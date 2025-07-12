"""
Nodos del agente de chatbot inteligente para Signaware.
Cada nodo representa una etapa del procesamiento de conversación.
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Configurar logging
logger = logging.getLogger(__name__)


class ChatbotNodes:

    def __init__(self):
        """Inicializa los nodos y sus dependencias."""
        self.logger = logging.getLogger(__name__)

    def classify_intent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Nodo para clasificar la intención del usuario.

        Args:
            state: Estado actual del chatbot

        Returns:
            Dict con la intención detectada
        """
        try:
            user_input = state.get("user_input", "")
            if not user_input:
                state["detected_intent"] = "GENERAL_QUERY"
                return state

            # Usar la instancia compartida del clasificador
            if hasattr(self, "intention_classifier"):
                classifier = self.intention_classifier
            else:
                # Fallback: crear nueva instancia si no está disponible
                from ..services.intention_classifier_service import (
                    IntentionClassifierService,
                )

                classifier = IntentionClassifierService()

            detected_intent = classifier.execute(user_input)

            state["detected_intent"] = detected_intent
            self.logger.info(f"Intención detectada: {detected_intent}")

            return state

        except Exception as e:
            self.logger.error(f"Error en classify_intent_node: {e}")
            state["detected_intent"] = "GENERAL_QUERY"
            return state

    # Nodos específicos por categoría de intención

    def hearing_aids_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo especializado para consultas sobre audífonos con RAG y scraping en tiempo real (wrapper síncrono)"""
        import asyncio
        
        try:
            # Ejecutar la versión asíncrona en un event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._hearing_aids_node_async(state))
            loop.close()
            return result
        except Exception as e:
            self.logger.error(f"Error en hearing_aids_node wrapper: {e}")
            state["response"] = (
                "¡Ups! 😅 No pude procesar tu consulta. ¿Me lo preguntas de otra forma? 💪"
            )
            return state
    
    async def _hearing_aids_node_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo especializado para consultas sobre audífonos con RAG y scraping en tiempo real (versión asíncrona)"""
        try:
            from ..providers.text_generation.text_generator_manager import (
                text_generator_manager,
            )
            from ..services.rag_service import RagService

            user_input = state.get("user_input", "")

            # Extraer información de ubicación y tipo de consulta del input del usuario
            location, specialty, search_type = self._extract_search_parameters(user_input)
            
            # Inicializar RAG Service
            rag_service = RagService()
            
            # Buscar audífonos similares usando RAG
            self.logger.info(f"🔍 Buscando audífonos similares para: '{user_input}'")
            similar_hearing_aids = rag_service.search_similar_hearing_aids(user_input, n_results=3)
            
            # Si no hay resultados en RAG, hacer scraping en tiempo real
            if not similar_hearing_aids:
                self.logger.info("🔄 No hay resultados en RAG, haciendo scraping en tiempo real...")
                similar_hearing_aids = await self._scrape_hearing_aids_realtime(user_input)
            
            # Generar prompt con información RAG y scraping en tiempo real
            prompt = self._generate_hearing_aids_rag_prompt(
                user_input, similar_hearing_aids, search_type
            )
            
            # Obtener el generador del estado o usar gemini por defecto
            generator = state.get("text_generator_model", "gemini")
            response = text_generator_manager.execute_generator(generator, prompt)
            state["response"] = response
            self._update_conversation_history(state, "HEARING_AIDS")

            return state

        except Exception as e:
            self.logger.error(f"Error en hearing_aids_node_async: {e}")
            state["response"] = (
                "¡Ups! 😅 No pude procesar tu consulta. ¿Me lo preguntas de otra forma? 💪"
            )
            return state

    def _extract_search_parameters(self, user_input: str) -> tuple:
        """Extrae parámetros de búsqueda del input del usuario"""
        import re
        
        # Ubicación por defecto
        location = "España"
        specialty = "audífonos"
        search_type = "centers"  # centers, advice, general
        
        # Detectar ubicación
        location_patterns = [
            r"en\s+([A-Za-zÀ-ÿ\s]+?)(?:\s+centros?|\s+especialistas?|\s+clínicas?)",
            r"([A-Za-zÀ-ÿ\s]+?)\s+centros?",
            r"([A-Za-zÀ-ÿ\s]+?)\s+especialistas?"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                break
        
        # Detectar tipo de consulta
        if any(word in user_input.lower() for word in ["consejo", "consejos", "mantenimiento", "cuidado", "limpiar", "limpieza"]):
            search_type = "advice"
        elif any(word in user_input.lower() for word in ["precio", "precios", "coste", "costo", "cuánto", "cuanto", "dinero"]):
            search_type = "prices"
        elif any(word in user_input.lower() for word in ["tecnología", "tecnologia", "moderno", "avanzado", "bluetooth", "wifi", "app"]):
            search_type = "technology"
        elif any(word in user_input.lower() for word in ["adaptación", "adaptacion", "adaptar", "nuevo", "primera vez"]):
            search_type = "adaptation"
        elif any(word in user_input.lower() for word in ["centro", "centros", "clínica", "clinica", "especialista", "doctor", "médico", "medico"]):
            search_type = "centers"
        elif any(word in user_input.lower() for word in ["noticia", "noticias", "actualidad", "nuevo", "último", "ultimo"]):
            search_type = "news"
        
        return location, specialty, search_type

    def _generate_hearing_aids_rag_prompt(self, user_input: str, similar_hearing_aids: List[Dict[str, Any]], search_type: str) -> str:
        """Genera un prompt específico con información RAG de audífonos"""
        
        # Preparar información de audífonos similares (RAG + Scraping)
        hearing_aids_info = ""
        if similar_hearing_aids:
            hearing_aids_info = "**🎧 Audífonos Recomendados (Información Actualizada):**\n\n"
            for i, hearing_aid in enumerate(similar_hearing_aids, 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                similarity_percent = int(hearing_aid['similarity_score'] * 100)
                hearing_aids_info += f"{emoji} **{hearing_aid['modelo']}** ({hearing_aid['marca']})\n"
                hearing_aids_info += f"📊 Similitud: {similarity_percent}%\n"
                if hearing_aid['tecnologias']:
                    hearing_aids_info += f"⚡ Tecnologías: {hearing_aid['tecnologias']}\n"
                if hearing_aid['conectividad']:
                    hearing_aids_info += f"📱 Conectividad: {hearing_aid['conectividad']}\n"
                hearing_aids_info += f"🔗 [Ver detalles]({hearing_aid['url']})\n"
                
                # Incluir información detallada del documento scrapeado
                if 'document' in hearing_aid and hearing_aid['document']:
                    hearing_aids_info += f"\n📋 **Información Detallada:**\n"
                    # Tomar los primeros 500 caracteres del documento para el prompt
                    doc_preview = hearing_aid['document'][:500]
                    hearing_aids_info += f"{doc_preview}...\n"
                
                hearing_aids_info += "\n"
        
        # Consejos específicos según el tipo de consulta
        advice_info = ""
        if search_type == "advice":
            advice_info = "💡 **Consejo de Mantenimiento:** Limpia regularmente tus audífonos y guárdalos en un lugar seco."
        elif search_type == "prices":
            advice_info = "💰 **Consejo de Precios:** Los precios varían según la tecnología. Consulta con especialistas para opciones de financiación."
        elif search_type == "technology":
            advice_info = "⚡ **Consejo de Tecnología:** Los audífonos modernos incluyen Bluetooth, apps y conectividad inteligente."
        elif search_type == "adaptation":
            advice_info = "🎯 **Consejo de Adaptación:** La adaptación puede tomar tiempo. Ten paciencia y consulta con tu especialista."
        elif search_type == "news":
            advice_info = "📰 **Consejo de Noticias:** Mantente informado sobre las últimas innovaciones en tecnología auditiva."
        else:
            # Consejo general
            advice_info = "💡 **Consejo General:** Consulta con un especialista para información personalizada."
        
        prompt = f"""
        Eres un amigable especialista en audífonos que ayuda a personas con discapacidad auditiva.
        
        El usuario pregunta: "{user_input}"
        
        **INFORMACIÓN DETALLADA DE AUDÍFONOS:**
        {hearing_aids_info}
        
        **CONSEJOS ÚTILES:**
        {advice_info}
        
        **INSTRUCCIONES IMPORTANTES:**
        
        1. **Si hay información de scraping en tiempo real**, incluye detalles específicos del audífono:
           - Características técnicas principales
           - Tecnologías incluidas
           - Beneficios específicos
           - Información de conectividad
        
        2. **Si hay información RAG**, menciona la similitud y características encontradas
        
        3. **Siempre incluye**:
           - Descripción detallada del audífono
           - Características técnicas relevantes
           - Beneficios para el usuario
           - Información de conectividad y tecnologías
           - Un consejo práctico específico
           - Un mensaje motivador
        
        4. **Formato de respuesta**:
           - Usa emojis para hacerlo atractivo
           - Sé específico con las características
           - Incluye información técnica relevante
           - Mantén un tono amigable y motivador
        
        5. **Si hay información del documento scrapeado**, incluye detalles específicos sobre:
           - Funcionalidades del audífono
           - Tecnologías integradas
           - Características de conectividad
           - Beneficios para la audición
        
        ¡Sé detallado, específico y motivador! 💪
        """
        
        return prompt
    
    async def _scrape_hearing_aids_realtime(self, user_input: str) -> List[Dict[str, Any]]:
        """
        Scraping en tiempo real de audífonos Phonak basado en la consulta del usuario.
        Usa las URLs almacenadas en la base de datos RAG.
        
        Args:
            user_input: Consulta del usuario
            
        Returns:
            Lista de audífonos con información detallada
        """
        try:
            from playwright.async_api import async_playwright
            from ..services.rag_service import RagService
            import re
            
            # Obtener URLs desde la base de datos RAG
            rag_service = RagService()
            rag_urls = rag_service.get_all_hearing_aid_urls()
            
            if not rag_urls:
                self.logger.warning("⚠️ No hay URLs en la base de datos RAG, usando URLs por defecto")
                # URLs específicas de modelos Phonak conocidos (fallback)
                phonak_urls = [
                    "https://www.phonak.com/es-es/dispositivos-auditivos/audifonos/virto-infinio",
                    "https://www.phonak.com/es-es/dispositivos-auditivos/audifonos/naida-paradise",
                    "https://www.phonak.com/es-es/dispositivos-auditivos/audifonos/sky-m",
                    "https://www.phonak.com/es-es/dispositivos-auditivos/audifonos/audeo-paradise",
                    "https://www.phonak.com/es-es/dispositivos-auditivos/audifonos/naida-marvel"
                ]
            else:
                self.logger.info(f"✅ Obtenidas {len(rag_urls)} URLs desde la base de datos RAG")
                phonak_urls = rag_urls
            
            # Buscar modelo específico por nombre en la base de datos RAG
            specific_model_url = self._find_specific_model_url(user_input, rag_service)
            
            if specific_model_url:
                self.logger.info(f"🎯 Modelo específico encontrado: {specific_model_url}")
                relevant_urls = [specific_model_url]
            else:
                # Filtrar URLs basado en la consulta del usuario
                relevant_urls = []
                user_input_lower = user_input.lower()
                
                for url in phonak_urls:
                    # Extraer nombre del modelo de la URL
                    model_name = url.split('/')[-1].replace('-', ' ').title()
                    
                    # Verificar si la consulta coincide con el modelo
                    if any(word in user_input_lower for word in model_name.lower().split()):
                        relevant_urls.append(url)
                    elif any(word in user_input_lower for word in ['bluetooth', 'wireless', 'recargable', 'smart']):
                        # Si busca características específicas, incluir todos
                        relevant_urls.append(url)
                
                # Si no hay coincidencias específicas, usar los primeros 2
                if not relevant_urls:
                    relevant_urls = phonak_urls[:2]
            
            self.logger.info(f"🔍 Scraping en tiempo real: {len(relevant_urls)} URLs relevantes")
            
            results = []
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                
                for url in relevant_urls:
                    try:
                        page = await browser.new_page()
                        await page.goto(url, timeout=30000)
                        await asyncio.sleep(3)
                        
                        # Extraer nombre del modelo
                        try:
                            h1_element = await page.query_selector("h1")
                            if h1_element:
                                model_name = await h1_element.inner_text()
                            else:
                                model_name = url.split('/')[-1].replace('-', ' ').title()
                        except:
                            model_name = url.split('/')[-1].replace('-', ' ').title()
                        
                        # Extraer todo el texto visible (como en tu scraper_phonak_model.py)
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
                                    if (
                                        esVisible(nodo) &&
                                        !excluir.includes(nodo.tagName) &&
                                        !nodo.closest('header, nav, footer')
                                    ) {
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
                        caracteristicas = self._extract_hearing_aid_features(texto_completo)
                        
                        # Calcular similitud basada en la consulta del usuario
                        similarity_score = self._calculate_similarity(user_input, texto_completo)
                        
                        results.append({
                            "modelo": model_name,
                            "url": url,
                            "marca": "Phonak",
                            "similarity_score": similarity_score,
                            "tecnologias": ", ".join(caracteristicas.get("tecnologia", [])),
                            "conectividad": ", ".join(caracteristicas.get("conectividad", [])),
                            "document": texto_completo[:1000] + "..." if len(texto_completo) > 1000 else texto_completo
                        })
                        
                        await page.close()
                        
                    except Exception as e:
                        self.logger.error(f"Error scraping {url}: {e}")
                        continue
                
                await browser.close()
            
            # Ordenar por similitud
            results.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            self.logger.info(f"✅ Scraping en tiempo real completado: {len(results)} audífonos")
            return results
            
        except Exception as e:
            self.logger.error(f"Error en scraping en tiempo real: {e}")
            return []
    
    def _extract_hearing_aid_features(self, texto: str) -> Dict[str, Any]:
        """Extrae características específicas del texto del audífono."""
        caracteristicas = {
            "tecnologia": [],
            "conectividad": [],
            "bateria": None,
            "resistencia_agua": None,
            "tamaño": None
        }
        
        texto_lower = texto.lower()
        
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
            ]
        }
        
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
    
    def _calculate_similarity(self, user_input: str, texto: str) -> float:
        """Calcula similitud entre la consulta del usuario y el texto del audífono."""
        user_words = set(user_input.lower().split())
        texto_words = set(texto.lower().split())
        
        # Calcular similitud simple basada en palabras comunes
        common_words = user_words.intersection(texto_words)
        similarity = len(common_words) / max(len(user_words), 1)
        
        return min(similarity, 1.0)  # Normalizar entre 0 y 1
    
    def _find_specific_model_url(self, user_input: str, rag_service) -> Optional[str]:
        """
        Busca un modelo específico por nombre en la base de datos RAG.
        
        Args:
            user_input: Consulta del usuario
            rag_service: Instancia del servicio RAG
            
        Returns:
            URL del modelo específico si se encuentra, None en caso contrario
        """
        try:
            # Nombres de modelos Phonak conocidos
            model_names = {
                "virto infinio": "virto-infinio",
                "virto infini": "virto-infinio", 
                "naida paradise": "naida-paradise",
                "sky m": "sky-m",
                "audeo paradise": "audeo-paradise",
                "naida marvel": "naida-marvel",
                "virto": "virto-infinio",
                "naida": "naida-paradise",
                "sky": "sky-m",
                "audeo": "audeo-paradise"
            }
            
            user_input_lower = user_input.lower()
            
            # Buscar coincidencias exactas de nombres de modelos
            for model_name, url_suffix in model_names.items():
                if model_name in user_input_lower:
                    self.logger.info(f"🎯 Modelo específico detectado: {model_name}")
                    
                    # Buscar en la base de datos RAG por nombre del modelo
                    search_results = rag_service.search_similar_hearing_aids(model_name, n_results=10)
                    
                    for result in search_results:
                        result_model = result.get('modelo', '').lower()
                        result_url = result.get('url', '')
                        
                        # Verificar si el resultado coincide con el modelo buscado
                        if (model_name in result_model or 
                            url_suffix in result_url or
                            any(word in result_model for word in model_name.split())):
                            self.logger.info(f"✅ URL específica encontrada: {result_url}")
                            return result_url
                    
                    # Si no se encuentra en RAG, construir URL por defecto
                    default_url = f"https://www.phonak.com/es-es/dispositivos-auditivos/audifonos/{url_suffix}"
                    self.logger.info(f"🔗 Usando URL por defecto: {default_url}")
                    return default_url
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error buscando modelo específico: {e}")
            return None

    def medical_center_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo especializado para centros médicos y especialistas con búsqueda web en tiempo real"""
        try:
            from ..providers.text_generation.text_generator_manager import (
                text_generator_manager,
            )
            from ..providers.web_search.web_search_provider import web_search_provider
            from ..providers.web_search.medical_news_provider import medical_news_provider

            user_input = state.get("user_input", "")

            # Extraer información de especialidad y ubicación del input del usuario
            self.logger.info(f"🔍 Procesando consulta médica: '{user_input}'")
            specialty, search_type, location = self._extract_medical_search_parameters(user_input)
            self.logger.info(f"🔬 Especialidad detectada: '{specialty}', Tipo: '{search_type}', Ubicación: '{location}'")
            
            # Realizar búsqueda web en tiempo real
            self.logger.info("🌐 Iniciando búsqueda de centros médicos...")
            search_results = web_search_provider.search_medical_centers(location=location, specialty=specialty)
            
            # Verificar si hay error en la búsqueda
            if "error" in search_results:
                self.logger.error(f"❌ Error en búsqueda: {search_results.get('error')}")
                state["response"] = f"¡Ups! 😅 {search_results.get('message', 'No se pudo completar la búsqueda.')} 💪"
                self._update_conversation_history(state, "MEDICAL_CENTER")
                return state
            
            self.logger.info(f"✅ Búsqueda completada. Fuente: {search_results.get('source', 'N/A')}, Centros encontrados: {search_results.get('total_results', 0)}")
            
            # Obtener noticias médicas actualizadas
            self.logger.info("📰 Obteniendo noticias médicas...")
            news_results = medical_news_provider.get_latest_hearing_aid_news(days=30)
            self.logger.info(f"✅ Noticias obtenidas. Artículos: {news_results.get('total_results', 0)}")
            
            # Generar prompt con información actualizada
            prompt = self._generate_medical_center_prompt(user_input, search_results, news_results, search_type)
            
            # Obtener el generador del estado o usar gemini por defecto
            generator = state.get("text_generator_model", "gemini")
            response = text_generator_manager.execute_generator(generator, prompt)
            state["response"] = response
            self._update_conversation_history(state, "MEDICAL_CENTER")

            return state

        except Exception as e:
            self.logger.error(f"Error en medical_center_node: {e}")
            state["response"] = (
                "¡Ups! 😅 No pude procesar tu consulta. ¿Me lo preguntas de otra forma? 💪"
            )
            return state

    def _extract_medical_search_parameters(self, user_input: str) -> tuple:
        """Extrae parámetros de búsqueda médica del input del usuario"""
        import re
        
        specialty = "centros auditivos"
        search_type = "centers"  # centers, specialists, hospitals, clinics
        location = None  # Por defecto None (usará Barcelona)
        
        # Detectar especialidad médica
        if any(word in user_input.lower() for word in ["otorrino", "otorrinolaringólogo", "otorrinolaringología", "centro auditivo", "centros auditivos", "audición", "oído", "oido"]):
            specialty = "centros auditivos"
        elif any(word in user_input.lower() for word in ["audiólogo", "audiología", "audífonos", "audifonos"]):
            specialty = "audiología"
        elif any(word in user_input.lower() for word in ["neurólogo", "neurología", "nervio auditivo"]):
            specialty = "neurología"
        elif any(word in user_input.lower() for word in ["pediatra", "pediatría", "niños", "niño", "infantil"]):
            specialty = "pediatría"
        elif any(word in user_input.lower() for word in ["geriatra", "geriatría", "mayores", "adultos mayores"]):
            specialty = "geriatría"
        
        # Detectar tipo de consulta
        if any(word in user_input.lower() for word in ["especialista", "doctor", "médico", "medico"]):
            search_type = "specialists"
        elif any(word in user_input.lower() for word in ["hospital", "hospitales"]):
            search_type = "hospitals"
        elif any(word in user_input.lower() for word in ["clínica", "clinica", "centro médico"]):
            search_type = "clinics"
        elif any(word in user_input.lower() for word in ["urgencias", "emergencia", "urgente"]):
            search_type = "emergency"
        elif any(word in user_input.lower() for word in ["revisión", "revision", "consulta", "cita"]):
            search_type = "appointment"
        else:
            search_type = "centers"
        
        # Detectar ubicación específica
        location_patterns = [
            r"en\s+([A-Za-zÀ-ÿ\s]+?)(?:\s+centros?|\s+especialistas?|\s+clínicas?|\s+hospitales?|\s+centro)",
            r"busca\s+(?:centros?|especialistas?|clínicas?|hospitales?)\s+en\s+([A-Za-zÀ-ÿ\s]+)",
            r"centros?\s+en\s+([A-Za-zÀ-ÿ\s]+)",
            r"especialistas?\s+en\s+([A-Za-zÀ-ÿ\s]+)",
            r"clínicas?\s+en\s+([A-Za-zÀ-ÿ\s]+)",
            r"hospitales?\s+en\s+([A-Za-zÀ-ÿ\s]+)"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                self.logger.info(f"📍 Ubicación detectada: '{location}'")
                break
        
        return specialty, search_type, location

    def _generate_medical_center_prompt(self, user_input: str, search_results: Dict[str, Any], news_results: Dict[str, Any], search_type: str) -> str:
        """Genera un prompt específico para centros médicos con información de búsqueda web"""
        
        # Preparar información de centros médicos
        centers_info = ""
        if "centers" in search_results and search_results["centers"]:
            centers_info = "**🏥 Centros Médicos Más Cercanos:**\n\n"
            for i, center in enumerate(search_results["centers"][:5], 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "4️⃣" if i == 4 else "5️⃣"
                centers_info += f"{emoji} **{center.get('name', 'Centro')}**\n"
                if center.get('address'):
                    centers_info += f"📍 {center.get('address')}\n"
                if center.get('phone'):
                    centers_info += f"📞 {center.get('phone')}\n"
                if center.get('website'):
                    centers_info += f"🌐 {center.get('website')}\n"
                if center.get('google_maps_url'):
                    centers_info += f"🗺️ [Ver en Google Maps]({center.get('google_maps_url')})\n"
                if center.get('rating'):
                    centers_info += f"⭐ {center.get('rating')}/5 ({center.get('reviews_count', 0)} reseñas)\n"
                centers_info += "\n"
        
        # Información de fuente
        source_info = f"**📡 Fuente:** {search_results.get('source', 'Búsqueda web')}"
        
        # Preparar información de noticias médicas
        news_info = ""
        if "articles" in news_results and news_results["articles"]:
            news_info = "**📰 Últimas Noticias Médicas:**\n\n"
            for i, article in enumerate(news_results["articles"][:2], 1):  # Top 2 noticias
                emoji = "📰" if i == 1 else "📋"
                news_info += f"{emoji} **{article.get('title', 'Noticia')}**\n"
                if article.get('description'):
                    news_info += f"📝 {article.get('description')[:100]}...\n"
                news_info += "\n"
        
        # Consejos específicos según el tipo de consulta
        advice_info = ""
        if search_type == "specialists":
            advice_info = """
            **👨‍⚕️ Consejos para Especialistas:**
            • Busca otorrinolaringólogos certificados
            • Pregunta por experiencia en tu caso específico
            • Consulta opiniones de otros pacientes
            • Verifica que acepte tu seguro médico
            """
        elif search_type == "hospitals":
            advice_info = """
            **🏥 Consejos para Hospitales:**
            • Lleva tu historial médico completo
            • Pregunta por especialistas en audición
            • Verifica horarios de atención
            • Ten preparados tus documentos de identidad
            """
        elif search_type == "clinics":
            advice_info = """
            **🏥 Consejos para Clínicas:**
            • Compara precios entre varias clínicas
            • Pregunta por equipos de diagnóstico
            • Verifica si tienen servicio de urgencias
            • Consulta por opciones de financiación
            """
        elif search_type == "emergency":
            advice_info = """
            **🚨 Consejos para Urgencias:**
            • Ve al hospital más cercano
            • Lleva identificación y tarjeta sanitaria
            • Explica claramente tus síntomas
            • Pide que te deriven a un especialista
            """
        elif search_type == "appointment":
            advice_info = """
            **📅 Consejos para Citas:**
            • Llama con anticipación para programar
            • Ten lista tu información médica
            • Lleva estudios previos si los tienes
            • Pregunta por la duración de la consulta
            """
        else:
            advice_info = """
            **💡 Consejo General:**
            • Busca centros con buena reputación
            • Verifica que tengan especialistas en audición
            • Compara opciones antes de decidir
            • Consulta por opciones de pago
            """
        
        prompt = f"""
        Eres un amigable especialista en salud auditiva que ayuda a personas con discapacidad auditiva.
        
        El usuario pregunta: "{user_input}"
        
        Responde de manera:
        - 🎉 Alegre y motivadora
        - 📝 Breve y fácil de entender
        - 💝 Amigable y empática
        - ✨ Con emojis y markdown para hacerlo más atractivo
        
        Información actualizada encontrada:
        {centers_info}
        {source_info}
        {news_info}
        {advice_info}
        
        **IMPORTANTE:** Si hay centros médicos encontrados, muestra SOLO:
        - Nombre del centro
        - Ubicación/dirección
        - Página web (si está disponible)
        
        No incluyas teléfonos ni puntuaciones en la respuesta principal.
        
        Da información práctica sobre:
        - Los centros médicos encontrados (nombre, ubicación, web)
        - Un consejo útil para la consulta
        - Un mensaje de apoyo
        
        ¡Sé positivo y alentador! 💪
        """
        
        return prompt

    def medical_news_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo especializado para noticias médicas y actualidad en salud auditiva"""
        try:
            from ..providers.text_generation.text_generator_manager import (
                text_generator_manager,
            )
            from ..providers.web_search.medical_news_provider import medical_news_provider

            user_input = state.get("user_input", "")

            # Extraer parámetros de búsqueda de noticias
            self.logger.info(f"📰 Procesando consulta de noticias: '{user_input}'")
            news_type, days = self._extract_news_parameters(user_input)
            self.logger.info(f"📰 Tipo de noticia: '{news_type}', Días: {days}")

            # Obtener noticias médicas actualizadas
            self.logger.info("📰 Obteniendo noticias médicas...")
            if news_type == "hearing_aids":
                news_results = medical_news_provider.get_latest_hearing_aid_news(days=days)
            elif news_type == "research":
                news_results = medical_news_provider.get_medical_research_news(days=days)
            elif news_type == "technology":
                news_results = medical_news_provider.get_medical_technology_news(days=days)
            else:
                news_results = medical_news_provider.get_latest_hearing_aid_news(days=days)

            self.logger.info(f"✅ Noticias obtenidas. Artículos: {news_results.get('total_results', 0)}")

            # Verificar si hay error en los resultados
            if "error" in news_results:
                self.logger.error(f"❌ Error en noticias: {news_results.get('message', 'Error desconocido')}")
                # Generar respuesta amigable cuando no hay noticias disponibles
                prompt = self._generate_medical_news_fallback_prompt(user_input, news_results, news_type)
            else:
                # Generar prompt con información de noticias
                prompt = self._generate_medical_news_prompt(user_input, news_results, news_type)

            # Obtener el generador del estado o usar gemini por defecto
            generator = state.get("text_generator_model", "gemini")
            response = text_generator_manager.execute_generator(generator, prompt)
            state["response"] = response
            self._update_conversation_history(state, "MEDICAL_NEWS")

            return state

        except Exception as e:
            self.logger.error(f"Error en medical_news_node: {e}")
            state["response"] = (
                "¡Ups! 😅 No pude procesar tu consulta de noticias. ¿Me lo preguntas de otra forma? 💪"
            )
            return state

    def _extract_news_parameters(self, user_input: str) -> tuple:
        """Extrae parámetros de búsqueda de noticias del input del usuario"""
        import re
        
        news_type = "hearing_aids"  # hearing_aids, research, technology
        days = 30  # Por defecto 30 días (límite del plan gratuito de News API)
        
        # Detectar tipo de noticia
        if any(word in user_input.lower() for word in ["investigación", "investigacion", "estudio", "estudios", "investigar"]):
            news_type = "research"
        elif any(word in user_input.lower() for word in ["tecnología", "tecnologia", "avances", "innovación", "innovacion", "nuevo", "nuevos"]):
            news_type = "technology"
        elif any(word in user_input.lower() for word in ["audífonos", "audifonos", "audición", "audicion", "oído", "oido"]):
            news_type = "hearing_aids"
        
        # Detectar período de tiempo
        if "últimos" in user_input.lower() or "last" in user_input.lower():
            days_match = re.search(r"(\d+)\s*días?", user_input.lower())
            if days_match:
                days = int(days_match.group(1))
        elif "hoy" in user_input.lower() or "today" in user_input.lower():
            days = 1
        elif "semana" in user_input.lower() or "week" in user_input.lower():
            days = 7
        elif "mes" in user_input.lower() or "month" in user_input.lower():
            days = 30
        elif "trimestre" in user_input.lower() or "quarter" in user_input.lower():
            days = 90
        elif "año" in user_input.lower() or "year" in user_input.lower():
            days = 365
        
        return news_type, days

    def _generate_medical_news_prompt(self, user_input: str, news_results: Dict[str, Any], news_type: str) -> str:
        """Genera un prompt específico para noticias médicas"""
        
        # Preparar información de noticias
        news_info = ""
        if "articles" in news_results and news_results["articles"]:
            news_info = "**📰 Últimas Noticias Médicas:**\n\n"
            for i, article in enumerate(news_results["articles"][:5], 1):  # Top 5 noticias
                emoji = "📰" if i == 1 else "📋" if i == 2 else "📄" if i == 3 else "📝" if i == 4 else "📌"
                news_info += f"{emoji} **{article.get('title', 'Noticia')}**\n"
                if article.get('description'):
                    news_info += f"📝 {article.get('description')[:150]}...\n"
                if article.get('source'):
                    news_info += f"📡 Fuente: {article.get('source')}\n"
                if article.get('published_at'):
                    news_info += f"📅 {article.get('published_at')}\n"
                news_info += "\n"
        
        # Información de fuente
        source_info = f"**📡 Fuente:** {news_results.get('source', 'Búsqueda de noticias médicas')}"
        
        # Consejos específicos según el tipo de noticia
        advice_info = ""
        if news_type == "research":
            advice_info = """
            **🔬 Consejos sobre Investigación:**
            • Mantente informado sobre los últimos avances
            • Consulta con tu especialista sobre nuevas opciones
            • Los estudios pueden abrir nuevas posibilidades de tratamiento
            """
        elif news_type == "technology":
            advice_info = """
            **⚡ Consejos sobre Tecnología:**
            • La tecnología avanza rápidamente en audífonos
            • Pregunta por las últimas innovaciones disponibles
            • Considera actualizar tu dispositivo si es necesario
            """
        else:
            advice_info = """
            **💡 Consejo General:**
            • Mantente al día con las noticias médicas
            • Consulta con profesionales sobre las novedades
            • La información actualizada puede mejorar tu tratamiento
            """
        
        prompt = f"""
        Eres un amigable especialista en salud auditiva que ayuda a personas con discapacidad auditiva.
        
        El usuario pregunta: "{user_input}"
        
        Responde de manera:
        - 🎉 Alegre y motivadora
        - 📝 Breve y fácil de entender
        - 💝 Amigable y empática
        - ✨ Con emojis y markdown para hacerlo más atractivo
        
        Información actualizada encontrada:
        {news_info}
        {source_info}
        {advice_info}
        
        Da información práctica sobre:
        - Las noticias más relevantes encontradas
        - Un consejo útil basado en las noticias
        - Un mensaje de apoyo y motivación
        
        ¡Sé positivo y alentador! 💪
        """
        
        return prompt

    def _generate_medical_news_fallback_prompt(self, user_input: str, news_results: Dict[str, Any], news_type: str) -> str:
        """Genera un prompt de fallback cuando no hay noticias disponibles"""
        
        # Obtener información de tendencias y consejos
        from ..providers.web_search.medical_news_provider import medical_news_provider
        
        trends_info = medical_news_provider.get_medical_trends()
        
        # Consejos específicos según el tipo de noticia
        advice_info = ""
        if news_type == "research":
            advice_info = """
            **🔬 Consejos sobre Investigación:**
            • Mantente informado sobre los últimos avances
            • Consulta con tu especialista sobre nuevas opciones
            • Los estudios pueden abrir nuevas posibilidades de tratamiento
            """
        elif news_type == "technology":
            advice_info = """
            **⚡ Consejos sobre Tecnología:**
            • La tecnología avanza rápidamente en audífonos
            • Pregunta por las últimas innovaciones disponibles
            • Considera actualizar tu dispositivo si es necesario
            """
        else:
            advice_info = """
            **💡 Consejo General:**
            • Mantente al día con las noticias médicas
            • Consulta con profesionales sobre las novedades
            • La información actualizada puede mejorar tu tratamiento
            """
        
        # Información sobre el error
        error_message = news_results.get('message', 'No se pudieron obtener noticias actualizadas')
        
        prompt = f"""
        Eres un amigable especialista en salud auditiva que ayuda a personas con discapacidad auditiva.
        
        El usuario pregunta: "{user_input}"
        
        IMPORTANTE: No se encontraron noticias específicas sobre audífonos en los últimos 30 días en las fuentes de noticias. Esto es normal porque las noticias sobre audífonos no son tan frecuentes como otros temas.
        
        Responde de manera:
        - 🎉 Alegre y motivadora
        - 📝 Breve y fácil de entender
        - 💝 Amigable y empática
        - ✨ Con emojis y markdown para hacerlo más atractivo
        
        IMPORTANTE: Debes decir claramente al usuario que no se encontraron noticias recientes sobre audífonos, pero que puedes compartir información útil sobre tendencias actuales.
        
        Estructura tu respuesta así:
        1. **Explica claramente** que no hay noticias recientes sobre audífonos
        2. **Comparte tendencias actuales** en lugar de noticias
        3. **Da un consejo útil** para mantenerse informado
        4. **Mensaje de apoyo** positivo
        
        Información disponible:
        {trends_info}
        {advice_info}
        
        ¡Sé positivo y alentador! 💪
        """
        
        return prompt

    def generate_image_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo especializado para generación de imágenes de audífonos usando Stable Diffusion"""
        try:
            from ..providers.image_generation.image_generator_manager import (
                image_generator_manager,
            )

            user_input = state.get("user_input", "")

            # Extraer parámetros específicos de audífonos del input del usuario
            self.logger.info(f"🎨 Procesando solicitud de imagen de audífono: '{user_input}'")
            hearing_aid_type, description = self._extract_hearing_aid_image_parameters(user_input)
            self.logger.info(f"🎨 Tipo de audífono: '{hearing_aid_type}', Descripción: '{description}'")

            # Obtener el generador de Stable Diffusion
            generator = image_generator_manager.get_generator("stable_diffusion")
            if not generator:
                state["response"] = "¡Ups! 😅 No está disponible el generador de imágenes. 💪"
                self._update_conversation_history(state, "GENERATE_IMAGE")
                return state

            # Generar imagen específica de audífonos
            self.logger.info("🎨 Iniciando generación de imagen de audífono...")
            result = generator.generate_hearing_aid_image(description)

            # Verificar si la generación fue exitosa
            if not result.get("success", False):
                self.logger.error(f"❌ Error en generación: {result.get('error', 'Error desconocido')}")
                state["response"] = f"¡Ups! 😅 {result.get('message', 'No se pudo generar la imagen del audífono.')} 💪"
                self._update_conversation_history(state, "GENERATE_IMAGE")
                return state

            # Obtener la imagen en base64
            image_base64 = result.get("image_base64")
            if not image_base64:
                state["response"] = "¡Ups! 😅 No se pudo generar la imagen del audífono. Intenta con otra descripción. 💪"
                self._update_conversation_history(state, "GENERATE_IMAGE")
                return state

            # Devolver objeto JSON con la estructura que espera el frontend
            response_obj = {
                "success": True,
                "image_base64": image_base64,
                "prompt": result.get("prompt", ""),
                "parameters": result.get("parameters", {}),
                "format": "base64",
                "hearing_aid_type": hearing_aid_type,
                "description": description
            }
            # Convertir el objeto a string JSON para que sea compatible con AIMessage
            import json
            state["response"] = json.dumps(response_obj)
            
            self.logger.info("✅ Imagen de audífono generada exitosamente")
            self._update_conversation_history(state, "GENERATE_IMAGE")

            return state

        except Exception as e:
            self.logger.error(f"Error en generate_image_node: {e}")
            state["response"] = (
                "¡Ups! 😅 No se pudo generar la imagen del audífono. ¿Me lo pides de otra forma? 💪"
            )
            return state

    def _extract_hearing_aid_image_parameters(self, user_input: str) -> tuple:
        """Extrae parámetros específicos de audífonos para generación de imágenes"""
        import re
        
        # Tipos de audífonos médicos para sordera reconocidos
        hearing_aid_types = {
            "behind_ear": ["detrás de la oreja", "detras de la oreja", "bte", "behind ear", "retroauricular", "audífono retroauricular"],
            "in_ear": ["dentro del oído", "dentro del oido", "ite", "in ear", "intraauricular", "audífono intraauricular"],
            "in_canal": ["en el canal", "canal auditivo", "cic", "in canal", "intracanal", "audífono intracanal"],
            "completely_in_canal": ["completamente en el canal", "cic", "completely in canal", "audífono completamente intracanal"],
            "receiver_in_canal": ["receptor en el canal", "ric", "receiver in canal", "audífono con receptor en canal"],
            "modern": ["moderno", "modern", "actual", "nuevo", "avanzado", "audífono moderno"],
            "wireless": ["inalámbrico", "wireless", "bluetooth", "sin cables", "audífono inalámbrico"],
            "rechargeable": ["recargable", "rechargeable", "batería recargable", "audífono recargable"],
            "discrete": ["discreto", "discrete", "invisible", "oculto", "pequeño", "audífono discreto"],
            "medical": ["médico", "medico", "para sordera", "discapacidad auditiva", "pérdida auditiva", "perdida auditiva"],
            "digital": ["digital", "tecnología digital", "procesamiento digital"],
            "smart": ["inteligente", "smart", "con app", "conectado"]
        }
        
        hearing_aid_type = "modern"  # Por defecto
        description = "modern hearing aid device"
        
        # Detectar tipo específico de audífono
        user_input_lower = user_input.lower()
        
        for type_name, keywords in hearing_aid_types.items():
            if any(keyword in user_input_lower for keyword in keywords):
                hearing_aid_type = type_name
                break
        
        # Extraer descripción específica del audífono
        hearing_patterns = [
            r"(?:audífono|audifono|dispositivo|imagen|genera|crea|dibuja|muestra)\s+(.+?)(?:\s+por favor|\s+gracias|\.|$)",
            r"genera\s+(?:un\s+)?(?:audífono|audifono|dispositivo)\s+(.+?)(?:\s+por favor|\s+gracias|$)",
            r"crea\s+(?:un\s+)?(?:audífono|audifono|dispositivo)\s+(.+?)(?:\s+por favor|\s+gracias|$)",
            r"dibuja\s+(?:un\s+)?(?:audífono|audifono|dispositivo)\s+(.+?)(?:\s+por favor|\s+gracias|$)"
        ]
        
        for pattern in hearing_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                extracted_desc = match.group(1).strip()
                if extracted_desc and len(extracted_desc) > 3:
                    description = extracted_desc
                break
        
        # Si no se encontró descripción específica, usar descripción por defecto según el tipo
        if description == "modern hearing aid device":
            type_descriptions = {
                "behind_ear": "medical behind the ear hearing aid device for hearing loss",
                "in_ear": "medical in the ear hearing aid device for hearing loss", 
                "in_canal": "medical in the canal hearing aid device for hearing loss",
                "completely_in_canal": "medical completely in canal hearing aid device for hearing loss",
                "receiver_in_canal": "medical receiver in canal hearing aid device for hearing loss",
                "modern": "modern medical hearing aid device for hearing loss",
                "wireless": "wireless bluetooth medical hearing aid device for hearing loss",
                "rechargeable": "rechargeable medical hearing aid device for hearing loss",
                "discrete": "discrete invisible medical hearing aid device for hearing loss",
                "medical": "medical hearing aid device for hearing loss and deafness",
                "digital": "digital medical hearing aid device for hearing loss",
                "smart": "smart medical hearing aid device for hearing loss"
            }
            description = type_descriptions.get(hearing_aid_type, "modern medical hearing aid device for hearing loss")
        
        # Limpiar descripción
        description = re.sub(r'(?:genera|crea|dibuja|muestra|imagen)\s+', '', description, flags=re.IGNORECASE)
        description = re.sub(r'\s+(?:por favor|gracias|\.)$', '', description, flags=re.IGNORECASE)
        
        return hearing_aid_type, description

    def _generate_image_prompt(self, image_type: str, description: str, user_input: str) -> str:
        """Genera un prompt optimizado para la generación de imágenes"""
        
        if image_type == "hearing_aid":
            return f"modern hearing aid device, {description}, professional product photography, clean background, high quality, detailed, realistic"
        elif image_type == "medical":
            return f"professional medical illustration, {description}, clean, detailed, educational, high quality, anatomical accuracy"
        elif image_type == "illustration":
            return f"professional illustration, {description}, clean, detailed, educational, high quality, artistic"
        else:
            return f"high quality image, {description}, clean, detailed, professional, realistic"

    def sound_report_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo especializado para reportes y análisis de sonidos"""
        try:
            from ..providers.text_generation.text_generator_manager import (
                text_generator_manager,
            )
            from ..services.sound_report_service import SoundReportService

            user_input = state.get("user_input", "")

            # Generar reporte de sonidos detectados
            sound_report_service = SoundReportService()

            # Extraer parámetros del usuario (si los especifica)
            days = 1  # Por defecto 1 día (hoy)
            user_id = None  # Por defecto todos los usuarios

            # Buscar parámetros en el input del usuario
            if "últimos" in user_input.lower() or "last" in user_input.lower():
                # Extraer número de días si se especifica
                import re

                days_match = re.search(r"(\d+)\s*días?", user_input.lower())
                if days_match:
                    days = int(days_match.group(1))
            elif "hoy" in user_input.lower() or "today" in user_input.lower():
                days = 1
            elif "semana" in user_input.lower() or "week" in user_input.lower():
                days = 7
            elif "mes" in user_input.lower() or "month" in user_input.lower():
                days = 30

            # Generar reporte
            report = sound_report_service.generate_sound_report(
                user_id=user_id, days=days
            )

            if "error" in report:
                # Si hay error, generar respuesta amigable
                prompt = f"""
                Eres un amigable especialista en sonidos que ayuda a personas con discapacidad auditiva.
                
                El usuario pregunta: "{user_input}"
                
                Hubo un pequeño problema técnico, pero puedes ayudarle con información básica.
                
                Responde de manera:
                - 🎉 Alegre y motivadora
                - 📝 Breve y fácil de entender
                - 💝 Amigable y empática
                - ✨ Con emojis para hacerlo más ameno
                
                Da información práctica sobre:
                - Una herramienta útil para detectar sonidos
                - Un consejo para estar más seguro
                
                Máximo 3-4 líneas. ¡Sé positivo y alentador!
                """

                # Obtener el generador del estado o usar gemini por defecto
                generator = state.get("text_generator_model", "gemini")
                response = text_generator_manager.execute_generator(generator, prompt)
                state["response"] = response
                self._update_conversation_history(state, "SOUND_REPORT")

                return state

            # Generar prompt con datos del reporte
            prompt = self._generate_sound_report_prompt(user_input, report)

            # Obtener el generador del estado o usar gemini por defecto
            generator = state.get("text_generator_model", "gemini")
            response = text_generator_manager.execute_generator(generator, prompt)
            state["response"] = response
            self._update_conversation_history(state, "SOUND_REPORT")

            return state

        except Exception as e:
            self.logger.error(f"Error en sound_report_node: {e}")
            state["response"] = (
                "¡Ups! 😅 No pude procesar tu consulta. ¿Me lo preguntas de otra forma? 💪"
            )
            return state

    def _generate_sound_report_prompt(
        self, user_input: str, report: Dict[str, Any]
    ) -> str:
        """Genera un prompt específico para el reporte de sonidos"""

        # Preparar datos del reporte
        summary = report.get("summary", {})
        sound_stats = report.get("sound_type_statistics", [])
        critical_sounds = report.get("critical_sounds", [])
        recommendations = report.get("recommendations", [])
        period = report.get("period", {})

        # Datos principales
        total_detections = summary.get("total_detections", 0)
        days = period.get("days", 30)

        # Top 5 sonidos más frecuentes
        top_sounds = ""
        if sound_stats:
            top_sounds = "**🎯 Top 5 Sonidos Detectados:**\n\n"
            for i, stat in enumerate(sound_stats[:5], 1):
                emoji = (
                    "🥇"
                    if i == 1
                    else "🥈" if i == 2 else "🥉" if i == 3 else "4️⃣" if i == 4 else "5️⃣"
                )
                top_sounds += (
                    f"{emoji} **{stat['label']}**: `{stat['count']} veces`\n\n"
                )

        # Sonido crítico reciente
        critical_info = ""
        if critical_sounds:
            critical_info = (
                f"**🚨 Última Alerta Crítica:** `{critical_sounds[0]['sound_type']}`"
            )

        # Recomendación principal
        main_recommendation = ""
        if recommendations:
            main_recommendation = (
                f"**💡 Recomendación Estrella:** > {recommendations[0]}"
            )

        prompt = f"""
        Eres un amigable especialista en sonidos que ayuda a personas con discapacidad auditiva.
        
        El usuario pregunta: "{user_input}"
        
        Responde de manera:
        - 🎉 Alegre y motivadora
        - 📝 Breve y directa (máximo 3 líneas)
        - 💝 Amigable y empática
        - ✨ Con emojis y markdown para hacerlo más atractivo
        
        Usa markdown para darle vida:
        - **Texto en negrita** para títulos importantes
        - `Código` para números o datos clave
        - > Citas para destacar información
        - Listas con • o - para organizar datos
        
        **Período del reporte:** {self._get_period_description(days)}
        
        Datos del reporte:
        - **📊 Total:** `{total_detections} detecciones` en `{days} días`
        {top_sounds}
        - {critical_info}
        - {main_recommendation}
        
        Da información práctica sobre:
        - Un dato importante del reporte
        - Una recomendación útil
        - Un mensaje de apoyo
        
        **Al final, agrega un chiste o dato curioso** basado en los sonidos detectados:
        - Compara dos tipos de sonidos de forma divertida
        - Menciona algo curioso sobre el patrón de sonidos
        - Haz una observación amigable sobre el entorno
        - Usa emojis y mantén el tono positivo
        
        ¡Sé positivo y alentador! 💪
        """

        return prompt

    def _get_period_description(self, days: int) -> str:
        """Genera una descripción amigable del período del reporte"""
        if days == 1:
            return "**📅 Hoy**"
        elif days == 7:
            return "**📅 Última semana**"
        elif days == 30:
            return "**📅 Último mes**"
        elif days == 90:
            return "**📅 Últimos 3 meses**"
        elif days == 365:
            return "**📅 Último año**"
        else:
            return f"**📅 Últimos {days} días**"

    def general_query_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo para consultas generales"""
        try:
            from ..providers.text_generation.text_generator_manager import (
                text_generator_manager,
            )

            user_input = state.get("user_input", "")

            prompt = f"""
            Eres un amigable asistente que ayuda a personas con discapacidad auditiva.
            
            El usuario pregunta: "{user_input}"
            
            Responde de manera:
            - 🎉 Alegre y motivadora
            - 📝 Breve y fácil de entender
            - 💝 Amigable y empática
            - ✨ Con emojis para hacerlo más ameno
            
            Da información práctica sobre:
            - Un recurso útil para su pregunta
            - Un consejo amigable
            - Un mensaje de apoyo
            
            Máximo 3-4 líneas. ¡Sé positivo y alentador!
            """

            # Obtener el generador del estado o usar gemini por defecto
            generator = state.get("text_generator_model", "gemini")
            response = text_generator_manager.execute_generator(generator, prompt)
            state["response"] = response
            self._update_conversation_history(state, "GENERAL_QUERY")

            return state

        except Exception as e:
            self.logger.error(f"Error en general_query_node: {e}")
            state["response"] = (
                "¡Ups! 😅 No pude procesar tu consulta. ¿Me lo preguntas de otra forma? 💪"
            )
            return state

    def _update_conversation_history(self, state: Dict[str, Any], detected_intent: str):
        """Actualiza el historial de conversación"""
        user_input = state.get("user_input", "")
        response = state.get("response", "")

        # Añadir mensajes al historial
        messages = state.get("messages", [])
        messages.append(HumanMessage(content=user_input))
        messages.append(AIMessage(content=response))
        state["messages"] = messages

        # Actualizar historial de conversación
        conversation_history = state.get("conversation_history", [])
        conversation_history.append(
            {
                "user_input": user_input,
                "detected_intent": detected_intent,
                "response": response,
            }
        )
        state["conversation_history"] = conversation_history
