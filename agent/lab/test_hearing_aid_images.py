"""
Script para probar la generación de imágenes de audífonos.
"""

import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.nodes.chatbot_nodes import ChatbotNodes

def test_hearing_aid_image_parameters():
    """Prueba la extracción de parámetros de imágenes de audífonos."""
    print("🧪 Probando extracción de parámetros de imágenes de audífonos...")
    
    # Crear instancia de nodos
    nodes = ChatbotNodes()
    
    # Casos de prueba específicos para audífonos médicos
    test_cases = [
        "Genera una imagen de un audífono médico para sordera",
        "Crea un audífono médico detrás de la oreja",
        "Dibuja un audífono médico inalámbrico con bluetooth",
        "Muéstrame un audífono médico recargable",
        "Imagen de audífono médico discreto",
        "Audífono médico dentro del oído",
        "Audífono médico en el canal auditivo",
        "Audífono médico para pérdida auditiva",
        "Audífono médico para discapacidad auditiva",
        "Audífono médico digital",
        "Audífono médico inteligente"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"🔍 Prueba {i}: '{test_input}'")
        print(f"{'='*60}")
        
        try:
            # Extraer parámetros
            hearing_aid_type, description = nodes._extract_hearing_aid_image_parameters(test_input)
            
            print(f"✅ Parámetros extraídos:")
            print(f"   Tipo: {hearing_aid_type}")
            print(f"   Descripción: {description}")
            
        except Exception as e:
            print(f"❌ Error en prueba {i}: {e}")
    
    print(f"\n{'='*60}")
    print("🏁 Prueba de extracción de parámetros completada")
    print(f"{'='*60}")

def test_image_generation():
    """Prueba la generación de imágenes de audífonos."""
    print("\n🧪 Probando generación de imágenes de audífonos...")
    
    # Crear instancia de nodos
    nodes = ChatbotNodes()
    
    # Casos de prueba específicos para audífonos médicos
    test_cases = [
        "Genera una imagen de un audífono médico para sordera",
        "Crea un audífono médico detrás de la oreja",
        "Dibuja un audífono médico inalámbrico"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"🔍 Prueba {i}: '{test_input}'")
        print(f"{'='*60}")
        
        try:
            # Estado de prueba
            test_state = {
                "user_input": test_input,
                "text_generator_model": "gemini"
            }
            
            # Ejecutar el nodo
            final_state = nodes.generate_image_node(test_state)
            
            print(f"✅ Nodo ejecutado exitosamente")
            
            # Verificar respuesta
            response = final_state.get("response", "")
            if response:
                print(f"📝 Respuesta generada (primeros 200 chars):")
                print(f"{response[:200]}...")
                
                # Verificar si es JSON válido
                try:
                    import json
                    response_obj = json.loads(response)
                    if response_obj.get("success"):
                        print(f"✅ Imagen generada exitosamente")
                        print(f"   Tipo: {response_obj.get('hearing_aid_type', 'N/A')}")
                        print(f"   Descripción: {response_obj.get('description', 'N/A')}")
                    else:
                        print(f"❌ Error en generación: {response_obj.get('error', 'Error desconocido')}")
                except json.JSONDecodeError:
                    print(f"⚠️ Respuesta no es JSON válido: {response}")
            else:
                print(f"❌ No se generó respuesta")
            
        except Exception as e:
            print(f"❌ Error en prueba {i}: {e}")
    
    print(f"\n{'='*60}")
    print("🏁 Prueba de generación de imágenes completada")
    print(f"{'='*60}")

def test_provider_methods():
    """Prueba los métodos específicos del provider de audífonos."""
    print("\n🧪 Probando métodos del provider de audífonos...")
    
    try:
        from agent.providers.image_generation.image_generator_manager import image_generator_manager
        
        # Obtener el generador
        generator = image_generator_manager.get_generator("stable_diffusion")
        
        if generator:
            print(f"✅ Generador disponible: {generator.__class__.__name__}")
            
            # Verificar si tiene el método específico
            if hasattr(generator, 'generate_hearing_aid_image'):
                print(f"✅ Método generate_hearing_aid_image disponible")
                
                # Probar generación
                result = generator.generate_hearing_aid_image("modern hearing aid device")
                
                if result.get("success"):
                    print(f"✅ Imagen de audífono generada exitosamente")
                    print(f"   Prompt: {result.get('prompt', 'N/A')}")
                    print(f"   Parámetros: {result.get('parameters', {})}")
                else:
                    print(f"❌ Error en generación: {result.get('error', 'Error desconocido')}")
            else:
                print(f"❌ Método generate_hearing_aid_image no disponible")
        else:
            print(f"❌ Generador no disponible")
            
    except Exception as e:
        print(f"❌ Error probando provider: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de imágenes de audífonos...")
    
    # Ejecutar pruebas
    test_hearing_aid_image_parameters()
    test_provider_methods()
    test_image_generation()
    
    print("\n✅ Todas las pruebas completadas") 