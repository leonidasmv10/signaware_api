# 🔍 Sistema de Búsqueda Web en Tiempo Real

Este módulo proporciona funcionalidad de búsqueda web en tiempo real para obtener información actualizada sobre centros médicos, noticias y consejos sobre audífonos.

## 🏗️ Arquitectura

### Providers

1. **WebSearchProvider** (`web_search_provider.py`)
   - Búsqueda de centros médicos usando Google Maps API
   - Scraping de directorios médicos web
   - Información de respaldo cuando las APIs no están disponibles

2. **MedicalNewsProvider** (`medical_news_provider.py`)
   - Búsqueda de noticias médicas usando News API
   - Base de datos de consejos médicos por tema
   - Tendencias actuales en salud auditiva

## 🚀 Funcionalidades

### Búsqueda de Centros Médicos

```python
from agent.providers.web_search.web_search_provider import web_search_provider

# Buscar centros en Madrid
centers = web_search_provider.search_medical_centers("Madrid", "audífonos")

# Resultado incluye:
# - Nombre del centro
# - Dirección
# - Teléfono
# - Puntuación
# - Sitio web
```

### Noticias Médicas

```python
from agent.providers.web_search.medical_news_provider import medical_news_provider

# Obtener noticias de los últimos 30 días
news = medical_news_provider.get_latest_hearing_aid_news(days=30)

# Consejos por tema
advice = medical_news_provider.get_medical_advice_by_topic("mantenimiento")
trends = medical_news_provider.get_medical_trends()
```

## 🔧 Configuración

### Variables de Entorno

```bash
# Google Maps API (opcional)
GOOGLE_MAPS_API_KEY=tu_api_key_aqui

# News API (opcional)
NEWS_API_KEY=tu_api_key_aqui
```

### Dependencias

```bash
pip install requests beautifulsoup4
```

## 📝 Uso en el Chatbot

Los nodos `hearing_aids_node` y `medical_center_node` ahora integran automáticamente:

1. **Detección de parámetros** del input del usuario:
   - Ubicación (ciudad, provincia)
   - Tipo de consulta (centros, precios, consejos, tecnología, etc.)
   - Especialidad médica (otorrinolaringología, audiología, etc.)

2. **Búsqueda web en tiempo real**:
   - Centros médicos cercanos
   - Noticias médicas actualizadas
   - Consejos específicos por tema

3. **Respuesta enriquecida**:
   - Información de centros encontrados
   - Noticias relevantes
   - Consejos personalizados
   - Tendencias actuales

## 🎯 Tipos de Consultas Soportadas

### Hearing Aids Node
| Tipo | Palabras Clave | Descripción |
|------|----------------|-------------|
| `centers` | centro, clínica, especialista, médico | Búsqueda de centros médicos |
| `prices` | precio, coste, dinero, cuánto | Información de precios |
| `advice` | consejo, mantenimiento, cuidado | Consejos prácticos |
| `technology` | tecnología, moderno, bluetooth | Tecnología actual |
| `adaptation` | adaptación, nuevo, primera vez | Proceso de adaptación |
| `news` | noticia, actualidad, último | Noticias recientes |

### Medical Center Node
| Tipo | Palabras Clave | Descripción |
|------|----------------|-------------|
| `specialists` | especialista, doctor, médico | Búsqueda de especialistas |
| `hospitals` | hospital, hospitales | Centros hospitalarios |
| `clinics` | clínica, centro médico | Clínicas especializadas |
| `emergency` | urgencias, emergencia, urgente | Servicios de urgencia |
| `appointment` | revisión, consulta, cita | Programación de citas |
| `centers` | centro, clínica | Centros médicos generales |

## 🔍 Ejemplos de Uso

### Consultas de Usuario

#### Hearing Aids Node
```
"Busco centros de audífonos en Barcelona"
→ Búsqueda de centros médicos en Barcelona

"¿Cuánto cuestan los audífonos?"
→ Información de precios y financiación

"Consejos para mantener mis audífonos"
→ Consejos de mantenimiento y cuidado

"¿Qué tecnología tienen los audífonos modernos?"
→ Información sobre tecnología actual

"Noticias sobre audífonos"
→ Últimas noticias médicas
```

#### Medical Center Node
```
"Busco especialistas en otorrinolaringología en Madrid"
→ Búsqueda de especialistas certificados

"¿Dónde hay hospitales con especialistas en audición?"
→ Centros hospitalarios con especialistas

"Necesito una clínica para revisión auditiva en Valencia"
→ Clínicas especializadas en audiología

"¿Hay urgencias para problemas de audición?"
→ Servicios de urgencia auditiva

"Quiero programar una cita con un audiólogo"
→ Consejos para programar citas médicas
```

### Respuestas Enriquecidas

El sistema genera respuestas que incluyen:

- 🏥 **Centros médicos** con dirección y contacto
- 📰 **Noticias actualizadas** sobre audífonos
- 💡 **Consejos específicos** según el tipo de consulta
- 📱 **Tendencias tecnológicas** actuales
- 🎯 **Recomendaciones personalizadas**

## 🛡️ Fallbacks y Robustez

El sistema incluye múltiples niveles de fallback:

1. **Google Maps API** → **Web Scraping** → **Información de Referencia**
2. **News API** → **Base de datos de noticias** → **Información de referencia**
3. **Errores de red** → **Timeouts** → **Respuestas locales**

## 🧪 Pruebas

Ejecuta el script de pruebas:

```bash
cd signaware_api/agent
python test_web_search.py
```

## 🔄 Integración con el Workflow

El sistema se integra automáticamente en el workflow del chatbot:

### Hearing Aids Node
1. **Clasificación de intención** → `HEARING_AIDS`
2. **Extracción de parámetros** → ubicación, tipo de consulta
3. **Búsqueda web** → centros, noticias, consejos
4. **Generación de respuesta** → información enriquecida
5. **Actualización del historial** → conversación persistente

### Medical Center Node
1. **Clasificación de intención** → `MEDICAL_CENTER`
2. **Extracción de parámetros** → ubicación, especialidad, tipo de centro
3. **Búsqueda web** → centros médicos, especialistas, hospitales
4. **Generación de respuesta** → información médica actualizada
5. **Actualización del historial** → conversación persistente

## 📊 Métricas y Monitoreo

El sistema registra:
- ✅ Búsquedas exitosas
- ❌ Errores de API
- ⏱️ Tiempos de respuesta
- 📍 Ubicaciones más consultadas
- 🔍 Tipos de consulta más populares

## 🚀 Próximas Mejoras

- [ ] Integración con más APIs de noticias
- [ ] Cache inteligente de búsquedas
- [ ] Geolocalización automática del usuario
- [ ] Recomendaciones personalizadas basadas en historial
- [ ] Integración con redes sociales para tendencias 