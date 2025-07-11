#!/usr/bin/env python3
"""
Script de prueba para el sistema de reportes de sonidos.
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.logic.chatbot_agent import ChatbotAgent


def test_sound_report():
    """Prueba el sistema de reportes de sonidos."""
    
    print("🔊 Probando Sistema de Reportes de Sonidos")
    print("=" * 60)
    
    # Inicializar el agente
    chatbot = ChatbotAgent()
    
    # Consultas de prueba para reportes de sonidos
    test_queries = [
        {
            "query": "¿Puedes generar un reporte de sonidos detectados?",
            "description": "Reporte general de sonidos"
        },
        {
            "query": "Necesito un reporte de los últimos 7 días de sonidos",
            "description": "Reporte de últimos 7 días"
        },
        {
            "query": "¿Qué sonidos críticos se han detectado?",
            "description": "Consulta sobre sonidos críticos"
        },
        {
            "query": "Muéstrame las estadísticas de detección de sonidos",
            "description": "Estadísticas de detección"
        },
        {
            "query": "¿Cuáles son los patrones de sonidos en mi entorno?",
            "description": "Análisis de patrones"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📝 Prueba {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        print("-" * 50)
        
        try:
            # Probar el método chat
            response = chatbot.chat(test_case['query'])
            
            print(f"🤖 Respuesta: {response['response'][:300]}...")
            print(f"📋 Intención detectada: {response['detected_intent']}")
            
            # Verificar que se detectó como SOUND_REPORT
            if response['detected_intent'] == "SOUND_REPORT":
                print("✅ Intención detectada correctamente como SOUND_REPORT")
            else:
                print(f"⚠️  Intención esperada: SOUND_REPORT, Detectada: {response['detected_intent']}")
            
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
    
    print("\n✅ Prueba de reportes de sonidos completada")


def test_sound_report_service():
    """Prueba directa del servicio de reportes de sonidos."""
    
    print("\n🔧 Probando Servicio de Reportes de Sonidos")
    print("=" * 60)
    
    try:
        from agent.services.sound_report_service import SoundReportService
        
        # Inicializar servicio
        service = SoundReportService()
        
        # Generar reporte
        report = service.generate_sound_report(days=30)
        
        print("📊 Reporte generado:")
        print(f"• Período: {report.get('period', {}).get('days', 30)} días")
        print(f"• Total de detecciones: {report.get('summary', {}).get('total_detections', 0)}")
        print(f"• Tipos únicos: {report.get('summary', {}).get('unique_sound_types', 0)}")
        print(f"• Confianza promedio: {report.get('summary', {}).get('average_confidence', 0):.3f}")
        
        # Mostrar sonidos más frecuentes
        sound_stats = report.get('sound_type_statistics', [])
        if sound_stats:
            print("\n🔊 Sonidos más detectados:")
            for i, stat in enumerate(sound_stats[:3], 1):
                print(f"{i}. {stat['label']}: {stat['count']} veces")
        
        # Mostrar recomendaciones
        recommendations = report.get('recommendations', [])
        if recommendations:
            print("\n💡 Recomendaciones:")
            for rec in recommendations:
                print(f"• {rec}")
        
        print("\n✅ Servicio de reportes funcionando correctamente")
        
    except Exception as e:
        print(f"❌ Error probando servicio: {e}")


if __name__ == "__main__":
    test_sound_report()
    test_sound_report_service() 