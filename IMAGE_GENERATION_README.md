# Generación de Imágenes con Stable Diffusion

Esta funcionalidad permite generar imágenes usando Stable Diffusion dentro de la aplicación Signaware.

## Características

- ✅ Generación de imágenes usando Stable Diffusion
- ✅ Soporte para imágenes médicas y de audífonos
- ✅ Conversión automática a base64
- ✅ Integración con el chatbot
- ✅ Interfaz web para descargar imágenes

## Instalación

### 1. Instalar dependencias

```bash
pip install diffusers torch torchvision
```

### 2. Verificar instalación

```bash
python test_image_generation.py
```

## Uso

### Desde el Chatbot

El chatbot puede generar imágenes automáticamente cuando detecta una solicitud de generación de imágenes. Ejemplos:

- "Genera un audífono moderno"
- "Crea una imagen de un oído"
- "Dibuja un dispositivo auditivo"
- "Muéstrame un audífono digital"

### Desde la API

```python
from agent.providers.image_generation.image_generator_manager import image_generator_manager

# Generar imagen básica
result = image_generator_manager.execute_generator("stable_diffusion", "modern hearing aid")

# Generar imagen médica
generator = image_generator_manager.get_generator("stable_diffusion")
result = generator.generate_medical_image("ear anatomy")

# Generar imagen de audífono
result = generator.generate_hearing_aid_image("digital hearing aid")
```

### Desde el Frontend

```javascript
import { imageGeneration } from './services/api';

const result = await imageGeneration("modern hearing aid device");
console.log(result.image_base64); // Imagen en base64
```

## Estructura del Proyecto

```
signaware_api/agent/providers/image_generation/
├── __init__.py
├── image_generation_provider.py      # Clase base
├── stable_diffusion_provider.py      # Implementación de Stable Diffusion
└── image_generator_manager.py        # Manager para coordinar generadores
```

## Configuración

### Modelo

Por defecto se usa el modelo `dreamlike-art/dreamlike-anime-1.0`. Para cambiar el modelo, modifica `stable_diffusion_provider.py`:

```python
self.pipe = StableDiffusionPipeline.from_pretrained(
    "tu-modelo-aqui",  # Cambiar por tu modelo preferido
    torch_dtype=torch.float16,
    use_safetensors=True
)
```

### Parámetros

Los parámetros por defecto son:
- `num_inference_steps`: 60
- `guidance_scale`: 8.5
- `output_type`: "pil"

Puedes modificarlos en `stable_diffusion_provider.py`.

## Tipos de Imágenes

### 1. Imágenes Generales
- Prompt: Descripción libre
- Uso: Cualquier tipo de imagen

### 2. Imágenes Médicas
- Prompt: Optimizado para ilustraciones médicas
- Uso: Anatomía, dispositivos médicos, etc.

### 3. Imágenes de Audífonos
- Prompt: Optimizado para productos auditivos
- Uso: Audífonos, dispositivos de audición

## Integración con el Chatbot

El chatbot detecta automáticamente las solicitudes de generación de imágenes y las rutea al nodo `generate_image_node`. El flujo es:

1. Usuario envía mensaje
2. Clasificador detecta intención `GENERATE_IMAGE`
3. Se ejecuta `generate_image_node`
4. Se genera la imagen con Stable Diffusion
5. Se devuelve la imagen en base64 junto con el texto

## Frontend

Las imágenes generadas se muestran en el chat con:
- Vista previa de la imagen
- Botón para descargar
- Información del prompt usado
- Estilos adaptados al tema (claro/oscuro)

## Troubleshooting

### Error: "No module named 'diffusers'"
```bash
pip install diffusers
```

### Error: CUDA out of memory
- Reduce `num_inference_steps` a 30-40
- Usa `torch.float16` en lugar de `torch.float32`
- Considera usar CPU si no tienes GPU

### Error: Modelo no carga
- Verifica conexión a internet
- Asegúrate de tener suficiente espacio en disco
- Revisa los logs para errores específicos

## Rendimiento

- **GPU**: ~10-30 segundos por imagen
- **CPU**: ~2-5 minutos por imagen
- **Memoria**: ~4-8GB VRAM requeridos

## Limitaciones

- Requiere GPU para rendimiento óptimo
- Las imágenes son representaciones artísticas
- No reemplaza consultas médicas profesionales
- El modelo puede generar contenido inapropiado

## Contribuir

Para agregar nuevos tipos de generadores de imágenes:

1. Crear nueva clase que herede de `ImageGenerationProvider`
2. Implementar métodos `execute()` e `is_available()`
3. Registrar en `ImageGeneratorManager`
4. Agregar tests en `test_image_generation.py` 