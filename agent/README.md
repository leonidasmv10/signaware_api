# Agente de Audio Inteligente - Signaware

Sistema de procesamiento de audio inteligente basado en LangGraph para la aplicación Signaware.

## 🎯 Descripción

Este agente utiliza LangGraph para crear un flujo de trabajo inteligente que:
1. **Graba audio** del entorno
2. **Analiza el tipo de sonido** usando YAMNet
3. **Transcribe conversaciones** cuando se detecta habla
4. **Proporciona respuestas estructuradas** con metadatos

## 🏗️ Arquitectura

### Estructura de Archivos
```
agent/
├── __init__.py
├── state.py          # Definición del estado del agente
├── nodes.py          # Nodos del workflow
├── workflow.py       # Configuración del grafo
├── views.py          # Endpoints de Django
├── urls.py           # Rutas URL
├── config.py         # Configuración del sistema
└── README.md         # Esta documentación
```

### Flujo de Trabajo
```
START → record_audio_node → audio_analysis_node → [decisión]
                                                    ↓
                                            ┌─────────────┐
                                            │ ¿Es Speech? │
                                            └─────────────┘
                                                    ↓
                                    ┌─────────────────────────┐
                                    │                         │
                                    ↓                         ↓
                        audio_transcription_node    show_sound_type_node
                                    ↓                         ↓
                                    └─────────┬───────────────┘
                                              ↓
                                             END
```

## 🚀 Endpoints Disponibles

### 1. Procesar Audio (Principal)
```http
POST /agent/process-audio/
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- audio: <archivo_de_audio>
```

**Respuesta:**
```json
{
  "success": true,
  "user_id": 1,
  "sound_type": "Speech",
  "confidence": 0.85,
  "is_conversation_detected": true,
  "transcription": "Hola, ¿cómo estás?",
  "messages": [
    {
      "type": "info",
      "content": "Audio grabado exitosamente en: /path/to/audio.wav"
    },
    {
      "type": "info", 
      "content": "Análisis completado: Speech (confianza: 0.85)"
    }
  ],
  "audio_path": "/path/to/audio.wav"
}
```

### 2. Health Check
```http
GET /agent/health/
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "status": "healthy",
  "workflow_compiled": true,
  "user_id": 1
}
```

### 3. Procesar Audio (Legacy)
```http
POST /agent/process-audio-legacy/
Content-Type: multipart/form-data

Form Data:
- audio: <archivo_de_audio>
```

## 📋 Tipos de Audio Soportados

- **WAV** (`audio/wav`)
- **MP3** (`audio/mp3`, `audio/mpeg`)
- **OGG** (`audio/ogg`)
- **FLAC** (`audio/flac`)

## 🎵 Tipos de Sonido Detectados

- **Speech** - Conversación humana
- **Music** - Música
- **Noise** - Ruido ambiental
- **Silence** - Silencio
- **Vehicle** - Sonidos de vehículos
- **Siren** - Sirenas de emergencia
- **Horn** - Bocinas
- **Unknown** - No identificado

## ⚙️ Configuración

### Parámetros de Audio
```python
AUDIO_CONFIG = {
    'duration': 3,        # Duración de grabación (segundos)
    'sample_rate': 16000, # Tasa de muestreo
    'channels': 1,        # Mono
    'format': 'wav',      # Formato de salida
    'verbose': False      # Modo debug
}
```

### Umbrales de Confianza
```python
CONFIDENCE_THRESHOLDS = {
    'speech_detection': 0.5,  # Mínimo para detectar conversación
    'high_confidence': 0.8,   # Confianza alta
    'medium_confidence': 0.6, # Confianza media
    'low_confidence': 0.3     # Confianza baja
}
```

## 🔧 Instalación y Uso

### 1. Dependencias Requeridas
```bash
pip install langgraph langchain-core
# + tus módulos de audio personalizados
```

### 2. Configuración de Carpetas
```python
from agent.config import create_directories
create_directories()  # Crea carpetas necesarias
```

### 3. Uso Básico
```python
from agent.workflow import compiled_workflow, get_initial_state

# Ejecutar el workflow
initial_state = get_initial_state()
final_state = compiled_workflow.invoke(initial_state)

# Obtener resultados
sound_type = final_state["sound_type"]
transcription = final_state["transcription"]
confidence = final_state["confidence"]
```

## 🐛 Manejo de Errores

### Errores Comunes
1. **Workflow no disponible**: Verificar que las dependencias estén instaladas
2. **Archivo de audio inválido**: Verificar formato y tamaño
3. **Error de transcripción**: Verificar que el audio contenga habla clara

### Logging
El sistema incluye logging detallado:
```python
import logging
logging.getLogger('agent').setLevel(logging.INFO)
```

## 🔒 Seguridad

- **Autenticación requerida** en todos los endpoints
- **Validación de tipos de archivo**
- **Límites de tamaño de archivo**
- **Limpieza de archivos temporales**

## 📈 Monitoreo

### Métricas Disponibles
- Tiempo de procesamiento
- Tasa de éxito de transcripción
- Tipos de sonido más comunes
- Niveles de confianza promedio

### Health Check
El endpoint `/agent/health/` proporciona:
- Estado del workflow
- Disponibilidad del sistema
- Información del usuario

## 🤝 Integración con Frontend

### Ejemplo de Uso con JavaScript
```javascript
const formData = new FormData();
formData.append('audio', audioBlob);

const response = await fetch('/agent/process-audio/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const result = await response.json();
console.log('Tipo de sonido:', result.sound_type);
console.log('Transcripción:', result.transcription);
```

## 🔄 Desarrollo

### Agregar Nuevos Nodos
1. Crear función en `nodes.py`
2. Agregar al workflow en `workflow.py`
3. Actualizar la lógica de decisión si es necesario

### Modificar Configuración
Editar `config.py` para ajustar:
- Parámetros de audio
- Umbrales de confianza
- Tipos de archivo permitidos
- Mensajes del sistema

## 📝 Notas

- El sistema está optimizado para audio de 3 segundos
- La transcripción solo se realiza si se detecta habla con confianza > 0.5
- Los archivos temporales se limpian automáticamente
- El sistema es thread-safe para múltiples usuarios

## 🆘 Soporte

Para problemas o preguntas:
1. Revisar los logs del sistema
2. Verificar la configuración en `config.py`
3. Probar el endpoint de health check
4. Verificar las dependencias de audio 