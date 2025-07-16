# 🎧 Signaware API

**Sistema de Inteligencia Artificial para Asistencia Auditiva**

Signaware API es una plataforma backend que utiliza múltiples modelos de inteligencia artificial para proporcionar asistencia integral a personas con discapacidad auditiva. El sistema combina detección de sonidos en tiempo real, procesamiento de lenguaje natural, generación de imágenes y análisis de audio.

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        DJANGO API                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Auth System   │  │  Audio Upload   │  │   Chat System   │ │
│  │   (JWT)         │  │  (File Upload)  │  │  (Messages)     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    AGENT MANAGER                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Sound Detector  │  │   Chatbot       │  │  Image Gen      │ │
│  │    Agent        │  │    Agent        │  │    Agent        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    AI MODELS LAYER                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐ │
│  │   YAMNet    │ │   Whisper   │ │   RAG       │ │  Stable  │ │
│  │  (Audio)    │ │(Transcribe) │ │ (Search)    │ │ Diffusion│ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    EXTERNAL APIS                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐ │
│  │   OpenAI    │ │   Gemini    │ │ HuggingFace │ │ ChromaDB │ │
│  │ (Embeddings)│ │ (Text Gen)  │ │ (Models)    │ │ (Vector) │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

La aplicación está construida con Django y utiliza un sistema de agentes de IA especializados:

- **Django REST API**: Backend principal con autenticación JWT
- **Agent Manager**: Coordina diferentes agentes de IA
- **Sound Detector Agent**: Procesa audio en tiempo real
- **Chatbot Agent**: Maneja conversaciones con IA
- **Image Generation Agent**: Crea imágenes con IA

## 🤖 Modelos de Inteligencia Artificial

### 🎵 **YAMNet - Análisis de Audio**
Detecta y clasifica sonidos en tiempo real usando el modelo YAMNet de Google. Identifica 521 tipos diferentes de sonidos y los categoriza en:
- 🔴 **Peligro**: Sirenas, alarmas, cristales rompiéndose
- 🟡 **Atención**: Teléfonos, timbres, silbatos
- 🟢 **Social**: Conversaciones, gritos, risas
- 🔵 **Ambiente**: Pasos, vehículos, animales

### 🗣️ **Whisper - Transcripción de Audio**
Convierte audio a texto usando Faster Whisper optimizado. Especializado en español y conversaciones.

### 🔍 **RAG - Sistema de Búsqueda Inteligente**
Sistema de Retrieval-Augmented Generation que combina:
- Web scraping en tiempo real de audífonos Phonak
- Embeddings vectoriales (OpenAI y HuggingFace)
- Base de datos vectorial ChromaDB
- Búsqueda semántica para recomendaciones

### 🎨 **Stable Diffusion - Generación de Imágenes**
Crea imágenes de audífonos y dispositivos médicos usando el modelo dreamlike-art/dreamlike-anime-1.0.

### 🧠 **Modelos de Generación de Texto**

#### **OpenAI GPT**
Modelo gpt-3.5-turbo para respuestas generales y análisis.

#### **Google Gemini**
Modelo gemini-2.0-flash para respuestas rápidas y contextuales.

#### **Modelo Fine-tuned (LeonidasMV)**
Modelo especializado en asistencia auditiva: `leonidasmv/mistral-7b-instruct-v0.3-auditory-assistant-finetuning`. Optimizado con quantización 8-bit para eficiencia.

### 🔤 **Sistema de Embeddings**
- **OpenAI**: text-embedding-ada-002 (1536 dimensiones)
- **HuggingFace**: all-MiniLM-L6-v2 (384 dimensiones)
- Sistema de fallback automático entre proveedores

## 🏛️ Arquitectura de Agentes

### **Sound Detector Agent**
Procesa audio en tiempo real:
- Análisis con YAMNet
- Transcripción con Whisper
- Clasificación de alertas
- Workflow automatizado

### **Chatbot Agent**
Maneja conversaciones inteligentes:
- Clasificación de intenciones
- Generación de respuestas
- Integración con RAG
- Búsqueda de información

### **Nodos Especializados**
- **Hearing Aids**: Consultas sobre audífonos
- **Medical Center**: Búsqueda de centros médicos
- **Medical News**: Noticias médicas
- **Image Generation**: Generación de imágenes

## 🔧 Configuración

### **Variables de Entorno Requeridas**
- OPENAI_API_KEY: Para embeddings y GPT
- GEMINI_API_KEY: Para generación de texto
- HF_EMBEDDING_MODEL: Modelo de HuggingFace
- SECRET_KEY: Clave secreta de Django

### **Dependencias Principales**
- Django y Django REST Framework
- TensorFlow y TensorFlow Hub (YAMNet)
- Faster Whisper (transcripción)
- Transformers (modelos de HuggingFace)
- ChromaDB (base de datos vectorial)
- Playwright (web scraping)

## 📡 Endpoints Principales

### **Autenticación**
- POST /api/auth/login/
- POST /api/auth/register/
- POST /api/auth/refresh/

### **Procesamiento de Audio**
- POST /api/agent/process-audio/

### **Chatbot**
- POST /api/agent/chat/

### **Generación de Imágenes**
- POST /api/agent/generate-image/

## 🚀 Instalación

### **1. Instalación de Dependencias**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121/
pip install -r requirements.txt
playwright install chromium
```

### **2. Configuración de Base de Datos**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py populate_soundcategories
python manage.py populate_sound_types
```

### **3. Actualizar Base de Datos RAG**
```bash
python manage.py update_hearing_aids_db
```

## 🧪 Testing

### **Scripts de Desarrollo**
```bash
python manage.py test
python -m agent.lab.test_rag_system
```

## 📊 Monitoreo

### **Métricas de Rendimiento**
- Tiempo de análisis de audio: ~2-3 segundos
- Precisión YAMNet: 85-95% en sonidos relevantes
- Tiempo de transcripción: ~1-2 segundos por 3s de audio
- Búsqueda RAG: <100ms para consultas
- Generación de imágenes: ~10-15 segundos

## 🔮 Roadmap

### **Próximas Características**
- Soporte para más marcas de audífonos
- Análisis de sentimientos en transcripciones
- Comparación automática de precios
- Recomendaciones personalizadas por perfil
- Actualización automática programada de RAG

### **Mejoras Técnicas**
- Cache inteligente para embeddings
- Compresión de vectores para optimización
- Sharding de base de datos para escalabilidad
- Monitoreo en tiempo real
- Tests automatizados

## 🤝 Contribución

### **Estructura del Proyecto**
```
signaware_api/
├── agent/                    # Agentes de IA
│   ├── logic/               # Lógica de agentes
│   ├── nodes/               # Nodos de workflow
│   ├── providers/           # Proveedores de IA
│   ├── services/            # Servicios especializados
│   ├── tools/               # Herramientas de procesamiento
│   └── workflows/           # Flujos de trabajo
├── core/                    # Modelos base
├── users/                   # Sistema de usuarios
└── chroma_db/              # Base de datos vectorial
```

### **Guidelines de Desarrollo**
1. Patrón Singleton para managers y servicios
2. Fallback automático en todos los proveedores de IA
3. Logging detallado para debugging y monitoreo
4. Validación de entrada en todos los endpoints
5. Manejo de errores con graceful degradation



---

**🎧 Signaware API** - Potenciando la accesibilidad auditiva con inteligencia artificial avanzada.