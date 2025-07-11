#!/usr/bin/env python3
"""
Script de prueba para el chatbot con nodos específicos por intención.
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.logic.chatbot_agent import ChatbotAgent


def test_specific_nodes():
    """Prueba el chatbot con diferentes tipos de consultas para verificar nodos específicos."""
    
    print("🤖 Probando Chatbot con Nodos Específicos por Intención")
    print("=" * 70)
    
    # Inicializar el agente
    chatbot = ChatbotAgent()
    
    # Consultas de prueba para cada categoría
    test_queries = [
        {
            "query": "¿Qué tipos de audífonos existen?",
            "expected_intent": "HEARING_AIDS",
            "description": "Consulta sobre audífonos"
        },
        {
            "query": "Necesito información sobre señales visuales para sordos",
            "expected_intent": "VISUAL_SIGNALS",
            "description": "Consulta sobre señales visuales"
        },
        {
            "query": "¿Hay alguna app que me ayude con la transcripción?",
            "expected_intent": "AUDIO_TRANSLATION",
            "description": "Consulta sobre transcripción"
        },
        {
            "query": "¿Qué centros médicos especializados conoces?",
            "expected_intent": "MEDICAL_CENTER",
            "description": "Consulta sobre centros médicos"
        },
        {
            "query": "¿Puedes recomendarme aplicaciones para sordos?",
            "expected_intent": "RECOMMEND_APP",
            "description": "Consulta sobre aplicaciones"
        },
        {
            "query": "¿Cuáles son mis derechos como persona con discapacidad auditiva?",
            "expected_intent": "KNOW_RIGHTS",
            "description": "Consulta sobre derechos"
        },
        {
            "query": "¿Dónde puedo obtener un certificado de discapacidad?",
            "expected_intent": "CERTIFICATE",
            "description": "Consulta sobre certificados"
        },
        {
            "query": "¿Cómo puedo analizar y reportar sonidos?",
            "expected_intent": "SOUND_REPORT",
            "description": "Consulta sobre análisis de sonidos"
        },
        {
            "query": "Hola, ¿cómo estás?",
            "expected_intent": "GENERAL_QUERY",
            "description": "Consulta general"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📝 Prueba {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        print(f"Intención esperada: {test_case['expected_intent']}")
        print("-" * 50)
        
        try:
            # Probar el método chat
            response = chatbot.chat(test_case['query'])
            
            print(f"🤖 Respuesta: {response['response'][:200]}...")
            print(f"📋 Intención detectada: {response['detected_intent']}")
            
            # Verificar si la intención coincide
            if response['detected_intent'] == test_case['expected_intent']:
                print("✅ Intención detectada correctamente")
            else:
                print(f"⚠️  Intención esperada: {test_case['expected_intent']}, Detectada: {response['detected_intent']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)
    
    # Probar el historial de conversación
    print("\n📚 Historial de conversación:")
    print("-" * 50)
    history = chatbot.get_conversation_history()
    for i, entry in enumerate(history, 1):
        print(f"{i}. Usuario: {entry['user_input']}")
        print(f"   Intención: {entry['detected_intent']}")
        print(f"   Respuesta: {entry['response'][:100]}...")
        print()
    
    # Probar el estado detallado
    print("\n📊 Estado detallado del agente:")
    print("-" * 50)
    status = chatbot.get_detailed_status()
    for key, value in status.items():
        print(f"{key}: {value}")
    
    print("\n✅ Prueba de nodos específicos completada")


if __name__ == "__main__":
    test_specific_nodes() 