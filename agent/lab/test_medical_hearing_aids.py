"""
Script para probar que el sistema genera específicamente audífonos médicos para sordera.
"""

import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.nodes.chatbot_nodes import ChatbotNodes

def test_medical_hearing_aid_detection():
    """Prueba que el sistema detecta correctamente audífonos médicos."""
    print("🧪 Probando detección de audífonos médicos...")
    
    # Crear instancia de nodos
    nodes = ChatbotNodes()
    
    # Casos de prueba específicos para audífonos médicos
    test_cases = [
        "Genera una imagen de un audífono médico para sordera",
        "Crea un audífono médico para pérdida auditiva",
        "Dibuja un audífono médico para discapacidad auditiva",
        "Muéstrame un audífono médico digital",
        "Audífono médico inteligente con app",
        "Audífono médico retroauricular",
        "Audífono médico intraauricular",
        "Audífono médico intracanal",
        "Audífono médico completamente intracanal",
        "Audífono médico con receptor en canal"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"🔍 Prueba {i}: '{test_input}'")
        print(f"{'='*70}")
        
        try:
            # Extraer parámetros
            hearing_aid_type, description = nodes._extract_hearing_aid_image_parameters(test_input)
            
            print(f"✅ Parámetros extraídos:")
            print(f"   Tipo: {hearing_aid_type}")
            print(f"   Descripción: {description}")
            
            # Verificar que la descripción incluye términos médicos
            medical_terms = ["medical", "hearing loss", "deafness", "hearing aid"]
            has_medical_terms = any(term in description.lower() for term in medical_terms)
            
            if has_medical_terms:
                print(f"✅ Descripción incluye términos médicos correctos")
            else:
                print(f"⚠️ Descripción no incluye términos médicos específicos")
            
        except Exception as e:
            print(f"❌ Error en prueba {i}: {e}")
    
    print(f"\n{'='*70}")
    print("🏁 Prueba de detección de audífonos médicos completada")
    print(f"{'='*70}")

def test_provider_medical_prompts():
    """Prueba que el provider genera prompts médicos correctos."""
    print("\n🧪 Probando prompts médicos del provider...")
    
    try:
        from agent.providers.image_generation.image_generator_manager import image_generator_manager
        
        # Obtener el generador
        generator = image_generator_manager.get_generator("stable_diffusion")
        
        if generator and hasattr(generator, 'generate_hearing_aid_image'):
            print(f"✅ Generador disponible con método médico")
            
            # Probar diferentes tipos de audífonos médicos
            medical_descriptions = [
                "medical hearing aid device for hearing loss",
                "medical behind the ear hearing aid device for hearing loss",
                "medical in the ear hearing aid device for hearing loss",
                "wireless bluetooth medical hearing aid device for hearing loss",
                "rechargeable medical hearing aid device for hearing loss"
            ]
            
            for i, description in enumerate(medical_descriptions, 1):
                print(f"\n🔍 Prueba {i}: {description}")
                
                try:
                    result = generator.generate_hearing_aid_image(description)
                    
                    if result.get("success"):
                        print(f"✅ Imagen médica generada exitosamente")
                        print(f"   Prompt: {result.get('prompt', 'N/A')}")
                        
                        # Verificar que el prompt incluye términos médicos
                        prompt = result.get('prompt', '').lower()
                        medical_indicators = [
                            'medical', 'hearing loss', 'deafness', 'medical device',
                            'medical equipment', 'hearing aid'
                        ]
                        
                        has_medical_terms = any(term in prompt for term in medical_indicators)
                        if has_medical_terms:
                            print(f"✅ Prompt incluye términos médicos correctos")
                        else:
                            print(f"⚠️ Prompt no incluye términos médicos específicos")
                            
                    else:
                        print(f"❌ Error en generación: {result.get('error', 'Error desconocido')}")
                        
                except Exception as e:
                    print(f"❌ Error en prueba {i}: {e}")
        else:
            print(f"❌ Generador o método no disponible")
            
    except Exception as e:
        print(f"❌ Error probando provider: {e}")

def test_negative_prompts():
    """Prueba que el sistema evita generar auriculares de música."""
    print("\n🧪 Probando que evita auriculares de música...")
    
    try:
        from agent.providers.image_generation.image_generator_manager import image_generator_manager
        
        generator = image_generator_manager.get_generator("stable_diffusion")
        
        if generator and hasattr(generator, 'generate_hearing_aid_image'):
            # Probar que el negative prompt incluye términos para evitar
            result = generator.generate_hearing_aid_image("medical hearing aid device for hearing loss")
            
            if result.get("success"):
                negative_prompt = result.get("negative_prompt", "")
                print(f"📋 Negative prompt: {negative_prompt}")
                
                # Verificar que incluye términos para evitar auriculares de música
                avoid_terms = [
                    "headphones", "earbuds", "music headphones", "gaming headset",
                    "wireless earbuds", "airpods", "earphones", "music device"
                ]
                
                has_avoid_terms = any(term in negative_prompt.lower() for term in avoid_terms)
                
                if has_avoid_terms:
                    print(f"✅ Negative prompt incluye términos para evitar auriculares de música")
                else:
                    print(f"⚠️ Negative prompt no incluye términos para evitar auriculares")
            else:
                print(f"❌ Error en generación: {result.get('error', 'Error desconocido')}")
        else:
            print(f"❌ Generador no disponible")
            
    except Exception as e:
        print(f"❌ Error probando negative prompts: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de audífonos médicos...")
    
    # Ejecutar pruebas
    test_medical_hearing_aid_detection()
    test_provider_medical_prompts()
    test_negative_prompts()
    
    print("\n✅ Todas las pruebas completadas") 