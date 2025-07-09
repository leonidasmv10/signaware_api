# Sistema de Filtrado de Sonidos Relevantes - Signaware

## 🎯 Descripción

El sistema de filtrado de sonidos relevantes permite que YAMNet detecte y clasifique automáticamente sonidos importantes del entorno, categorizándolos según su nivel de urgencia y tipo de alerta.

## 🔧 Configuración

### Diccionario de Sonidos Relevantes

El sistema utiliza un diccionario predefinido que mapea sonidos específicos a categorías de alerta:

```python
RELEVANT_SOUNDS_DICT = {
    'Alarm': 'danger_alert',
    'Fire alarm': 'danger_alert',
    'Siren': 'danger_alert',
    'Vehicle horn': 'danger_alert',
    'Speech': 'social_alert',
    'Children shouting': 'social_alert',
    'Footsteps': 'environment_alert',
    'Door': 'environment_alert',
    # ... más sonidos
}
```

### Categorías de Alerta

- **🔴 `danger_alert`**: Sonidos que indican peligro inmediato
  - Alarmas de incendio
  - Sirenas de emergencia
  - Bocinas de vehículos
  - Cristales rompiéndose

- **🟡 `attention_alert`**: Sonidos que requieren atención
  - Timbres de puerta
  - Teléfonos sonando
  - Golpes en puertas

- **🟢 `social_alert`**: Actividad social detectada
  - Habla humana
  - Conversaciones
  - Risa de niños
  - Llanto de bebés

- **🔵 `environment_alert`**: Cambios en el entorno
  - Pasos
  - Puertas abriéndose/cerrándose
  - Sonidos de vehículos
  - Actividad ambiental

## 🚀 Funcionalidades

### 1. Filtrado Automático

El sistema filtra automáticamente los sonidos detectados por YAMNet, mostrando solo aquellos que están en el diccionario de sonidos relevantes.

### 2. Categorización Inteligente

Cada sonido detectado se clasifica automáticamente en una de las cuatro categorías de alerta según su naturaleza.

### 3. Notificaciones Visuales

El frontend muestra notificaciones visuales con:
- Iconos específicos por categoría
- Colores diferenciados
- Información de confianza
- Transcripción (si aplica)

### 4. Configuración Flexible

```python
SOUND_FILTER_CONFIG = {
    'enabled': True,  # Habilitar/deshabilitar filtro
    'min_confidence': 0.3,  # Confianza mínima
    'include_unknown': False,  # Incluir sonidos no clasificados
}
```

## 📊 Flujo de Procesamiento

1. **Grabación de Audio**: El sistema graba audio del entorno
2. **Análisis YAMNet**: YAMNet analiza el audio y detecta sonidos
3. **Filtrado**: Solo se procesan sonidos relevantes del diccionario
4. **Categorización**: Cada sonido se clasifica según su tipo
5. **Notificación**: Se muestra alerta visual en el frontend
6. **Registro**: Se guarda en el chat con información detallada

## 🎨 Interfaz de Usuario

### Alertas en Tiempo Real

Las alertas aparecen en la esquina superior derecha con:
- Icono de categoría (🔴🟡🟢🔵)
- Título descriptivo
- Tipo de sonido detectado
- Nivel de confianza
- Hora de detección
- Transcripción (si es conversación)

### Mensajes en Chat

Los sonidos relevantes se registran en el chat con:
- Formato markdown
- Información detallada
- Recomendaciones de seguridad
- Enlaces a audio (si está disponible)

## ⚙️ Configuración Avanzada

### Agregar Nuevos Sonidos

Para agregar nuevos sonidos al diccionario:

```python
# En config.py
RELEVANT_SOUNDS_DICT['Nuevo sonido'] = 'categoria_alert'
```

### Modificar Categorías

```python
SOUND_FILTER_CONFIG['alert_categories'] = {
    'danger_alert': '🔴 Peligro',
    'attention_alert': '🟡 Atención',
    'social_alert': '🟢 Social',
    'environment_alert': '🔵 Entorno'
}
```

### Ajustar Sensibilidad

```python
SOUND_FILTER_CONFIG['min_confidence'] = 0.5  # Más estricto
SOUND_FILTER_CONFIG['min_confidence'] = 0.2  # Más sensible
```

## 🔍 Ejemplos de Uso

### Detección de Alarma de Incendio
```
🔴 ¡ALERTA DE PELIGRO!
🚨 Sonido: Fire alarm
📊 Confianza: 85%
🚨 Recomendación: Mantén la atención y verifica tu entorno.
```

### Conversación Detectada
```
🟢 ACTIVIDAD SOCIAL DETECTADA
🗣️ Sonido: Speech
📊 Confianza: 92%
💬 Transcripción: "Hola, ¿cómo estás?"
```

### Cambio en el Entorno
```
🔵 CAMBIO EN EL ENTORNO
👣 Sonido: Footsteps
📊 Confianza: 78%
```

## 🛠️ Mantenimiento

### Logs del Sistema

El sistema registra todas las detecciones:
```
[INFO] ✅ Sonido relevante detectado: Fire alarm (danger_alert) - Confianza: 0.850
[INFO] 🎯 Sonidos relevantes filtrados para audio_20241201_143022.wav:
[INFO]    🔴 Fire alarm: 0.850 (danger_alert)
```

### Monitoreo de Rendimiento

- Verificar confianza promedio de detecciones
- Revisar falsos positivos/negativos
- Ajustar umbrales según necesidades

## 🔮 Futuras Mejoras

1. **Aprendizaje Automático**: Entrenar modelos específicos para cada categoría
2. **Personalización**: Permitir a usuarios configurar sus propios sonidos relevantes
3. **Análisis Temporal**: Detectar patrones de sonidos a lo largo del tiempo
4. **Integración IoT**: Conectar con sensores adicionales del entorno
5. **Notificaciones Push**: Enviar alertas a dispositivos móviles

## 📝 Notas Técnicas

- **Umbral de Confianza**: 0.3 por defecto (ajustable)
- **Frecuencia de Análisis**: Cada 3 segundos en modo automático
- **Formato de Audio**: WAV, 16kHz, mono
- **Modelo**: YAMNet de Google
- **Compatibilidad**: Funciona con todos los navegadores modernos 