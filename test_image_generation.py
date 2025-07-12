#!/usr/bin/env python3
"""
Script de prueba para la generación de imágenes usando Stable Diffusion.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signaware_api.settings')
django.setup()

from agent.providers.image_generation.image_generator_manager import image_generator_manager


def test_image_generation():
    """Prueba la generación de imágenes."""
    print("🎨 Probando generación de imágenes...")
    
    try:
        # Verificar si el generador está disponible
        if not image_generator_manager.is_generator_available("stable_diffusion"):
            print("❌ El generador de Stable Diffusion no está disponible")
            return False
        
        print("✅ Generador de Stable Diffusion disponible")
        
        # Probar generación de imagen
        prompt = "modern hearing aid device, professional product photography, clean background, high quality, detailed"
        
        print(f"🎨 Generando imagen con prompt: '{prompt}'")
        
        result = image_generator_manager.execute_generator("stable_diffusion", prompt)
        
        if result.get("success", False):
            print("✅ Imagen generada exitosamente")
            print(f"📊 Parámetros: {result.get('parameters', {})}")
            print(f"📏 Tamaño base64: {len(result.get('image_base64', ''))} caracteres")
            return True
        else:
            print(f"❌ Error en generación: {result.get('error', 'Error desconocido')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False


def test_medical_image():
    """Prueba la generación de imágenes médicas."""
    print("\n🏥 Probando generación de imagen médica...")
    
    try:
        # Obtener el generador
        generator = image_generator_manager.get_generator("stable_diffusion")
        
        # Probar generación de imagen médica
        result = generator.generate_medical_image("ear anatomy, clean illustration")
        
        if result.get("success", False):
            print("✅ Imagen médica generada exitosamente")
            return True
        else:
            print(f"❌ Error en generación médica: {result.get('error', 'Error desconocido')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba médica: {e}")
        return False


def test_hearing_aid_image():
    """Prueba la generación de imágenes de audífonos."""
    print("\n🔊 Probando generación de imagen de audífono...")
    
    try:
        # Obtener el generador
        generator = image_generator_manager.get_generator("stable_diffusion")
        
        # Probar generación de imagen de audífono
        result = generator.generate_hearing_aid_image("modern digital hearing aid")
        
        if result.get("success", False):
            print("✅ Imagen de audífono generada exitosamente")
            return True
        else:
            print(f"❌ Error en generación de audífono: {result.get('error', 'Error desconocido')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de audífono: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Iniciando pruebas de generación de imágenes...")
    
    # Ejecutar pruebas
    test1 = test_image_generation()
    test2 = test_medical_image()
    test3 = test_hearing_aid_image()
    
    print(f"\n📊 Resultados de las pruebas:")
    print(f"   - Generación básica: {'✅' if test1 else '❌'}")
    print(f"   - Imagen médica: {'✅' if test2 else '❌'}")
    print(f"   - Imagen de audífono: {'✅' if test3 else '❌'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.") 