"""
Proveedor de generación de imágenes usando Stable Diffusion.
"""

import os
import base64
import io
import logging
from typing import Dict, Any, Optional
import torch
from PIL import Image

from .image_generation_provider import ImageGenerationProvider

# Configurar logging
logger = logging.getLogger(__name__)


class StableDiffusionProvider(ImageGenerationProvider):
    """
    Proveedor de generación de imágenes usando Stable Diffusion.
    Utiliza el modelo dreamlike-art/dreamlike-anime-1.0 para generar imágenes.
    """
    
    def __init__(self):
        """Inicializa el proveedor de Stable Diffusion."""
        self.logger = logging.getLogger(__name__)
        self.pipe = None
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Carga el modelo de Stable Diffusion."""
        try:
            from diffusers import StableDiffusionPipeline
            
            self.logger.info("🔄 Cargando modelo Stable Diffusion...")
            
            # Cargar el pipeline de Stable Diffusion
            self.pipe = StableDiffusionPipeline.from_pretrained(
                "dreamlike-art/dreamlike-anime-1.0",
                torch_dtype=torch.float16,
                use_safetensors=True
            )
            
            # Mover a GPU si está disponible
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.pipe.to(device)
            
            self.model_loaded = True
            self.logger.info(f"✅ Modelo cargado exitosamente en {device}")
            
        except ImportError as e:
            self.logger.error(f"❌ Error importando diffusers: {e}")
            self.logger.error("Instala diffusers con: pip install diffusers")
            self.model_loaded = False
        except Exception as e:
            self.logger.error(f"❌ Error cargando modelo: {e}")
            self.model_loaded = False
    
    def is_available(self) -> bool:
        """
        Verifica si el proveedor está disponible.
        
        Returns:
            bool: True si el modelo está cargado, False en caso contrario
        """
        return self.model_loaded and self.pipe is not None
    
    def execute(self, prompt: str, negative_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Genera una imagen usando Stable Diffusion.
        
        Args:
            prompt: Descripción de la imagen a generar
            negative_prompt: Descripción de lo que NO debe aparecer en la imagen
            **kwargs: Parámetros adicionales (num_inference_steps, guidance_scale, etc.)
            
        Returns:
            Dict con la imagen en base64 y metadatos
        """
        if not self.is_available():
            raise RuntimeError("El modelo de Stable Diffusion no está disponible")
        
        try:
            self.logger.info(f"🎨 Generando imagen con prompt: '{prompt[:50]}...'")
            
            # Parámetros por defecto
            num_inference_steps = kwargs.get('num_inference_steps', 60)
            guidance_scale = kwargs.get('guidance_scale', 8.5)
            
            # Negative prompt por defecto si no se proporciona
            if negative_prompt is None:
                negative_prompt = "blurry, low quality, distorted, deformed, ugly, bad anatomy"
            
            # Generar la imagen
            result = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                output_type="pil"
            )
            
            # Obtener la primera imagen
            image = result.images[0]
            
            # Convertir a base64
            image_base64 = self._image_to_base64(image)
            
            self.logger.info("✅ Imagen generada exitosamente")
            
            return {
                "success": True,
                "image_base64": image_base64,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "parameters": {
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale,
                    "model": "dreamlike-art/dreamlike-anime-1.0"
                },
                "format": "base64"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error generando imagen: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "No se pudo generar la imagen"
            }
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """
        Convierte una imagen PIL a base64.
        
        Args:
            image: Imagen PIL
            
        Returns:
            str: Imagen codificada en base64
        """
        try:
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Guardar en buffer
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Codificar en base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return image_base64
            
        except Exception as e:
            self.logger.error(f"❌ Error convirtiendo imagen a base64: {e}")
            raise
    
    def generate_medical_image(self, description: str) -> Dict[str, Any]:
        """
        Genera una imagen relacionada con medicina/audición.
        
        Args:
            description: Descripción de la imagen médica
            
        Returns:
            Dict con la imagen generada
        """
        # Prompt optimizado para imágenes médicas
        medical_prompt = f"professional medical illustration, {description}, clean, detailed, educational, high quality"
        medical_negative = "cartoon, anime, blurry, low quality, distorted, deformed, ugly, bad anatomy, gore, blood"
        
        return self.execute(
            prompt=medical_prompt,
            negative_prompt=medical_negative,
            num_inference_steps=50,
            guidance_scale=7.5
        )
    
    def generate_hearing_aid_image(self, description: str = "medical hearing aid device for hearing loss") -> Dict[str, Any]:
        """
        Genera una imagen de audífonos médicos para sordera.
        
        Args:
            description: Descripción específica del audífono médico
            
        Returns:
            Dict con la imagen generada
        """
        # Prompt específico para audífonos médicos (no auriculares de música)
        hearing_prompt = f"medical hearing aid device for hearing loss and deafness, {description}, professional medical device photography, clean background, high quality, detailed, realistic, medical equipment"
        hearing_negative = "cartoon, anime, blurry, low quality, distorted, deformed, ugly, bad anatomy, multiple devices, headphones, earbuds, music headphones, gaming headset, wireless earbuds, airpods, earphones, music device, entertainment device"
        
        return self.execute(
            prompt=hearing_prompt,
            negative_prompt=hearing_negative,
            num_inference_steps=50,
            guidance_scale=7.5
        ) 