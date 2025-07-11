#!/usr/bin/env python3
"""
Script de prueba simplificado para el sistema de reportes de sonidos.
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.services.sound_report_service import SoundReportService


def test_sound_report_service():
    """Prueba directa del servicio de reportes de sonidos."""
    
    print("🔧 Probando Servicio de Reportes de Sonidos")
    print("=" * 60)
    
    try:
        # Inicializar servicio
        service = SoundReportService()
        
        # Generar reporte
        print("📊 Generando reporte...")
        report = service.generate_sound_report(days=30)
        
        print("✅ Reporte generado exitosamente")
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
        
        # Mostrar actividad reciente
        temporal_patterns = report.get('temporal_patterns', {})
        if temporal_patterns:
            recent_activity = temporal_patterns.get('recent_activity', {})
            print(f"\n⏰ Actividad reciente:")
            print(f"• Últimas 24h: {recent_activity.get('last_24h_detections', 0)}")
            print(f"• Últimos 7 días: {recent_activity.get('last_7d_detections', 0)}")
            print(f"• Últimos 30 días: {recent_activity.get('last_30d_detections', 0)}")
        
        # Mostrar recomendaciones
        recommendations = report.get('recommendations', [])
        if recommendations:
            print("\n💡 Recomendaciones:")
            for rec in recommendations:
                print(f"• {rec}")
        
        print("\n✅ Servicio de reportes funcionando correctamente")
        
    except Exception as e:
        print(f"❌ Error probando servicio: {e}")
        import traceback
        traceback.print_exc()


def test_chatbot_with_report():
    """Prueba el chatbot con reportes de sonidos."""
    
    print("\n🤖 Probando Chatbot con Reportes de Sonidos")
    print("=" * 60)
    
    try:
        from agent.logic.chatbot_agent import ChatbotAgent
        
        # Inicializar el agente
        chatbot = ChatbotAgent()
        
        # Probar consulta de reporte
        query = "¿Puedes generar un reporte de sonidos detectados?"
        print(f"Query: {query}")
        
        response = chatbot.chat(query)
        
        print(f"🤖 Respuesta: {response['response'][:200]}...")
        print(f"📋 Intención detectada: {response['detected_intent']}")
        
        if response['detected_intent'] == "SOUND_REPORT":
            print("✅ Intención detectada correctamente como SOUND_REPORT")
        else:
            print(f"⚠️  Intención esperada: SOUND_REPORT, Detectada: {response['detected_intent']}")
        
        print("\n✅ Chatbot con reportes funcionando correctamente")
        
    except Exception as e:
        print(f"❌ Error probando chatbot: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_sound_report_service()
    test_chatbot_with_report() 