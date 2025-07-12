"""
Script de prueba para demostrar la funcionalidad de búsqueda web en tiempo real.
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signaware_api.settings')
django.setup()

from agent.providers.web_search.web_search_provider import web_search_provider
from agent.providers.web_search.medical_news_provider import medical_news_provider
from agent.nodes.chatbot_nodes import ChatbotNodes

def test_web_search_functionality():
    """Prueba la funcionalidad de búsqueda web"""
    
    print("🔍 Probando búsqueda web en tiempo real...\n")
    
    # 1. Probar búsqueda de centros médicos
    print("1️⃣ Búsqueda de centros médicos en Madrid:")
    try:
        centers = web_search_provider.search_medical_centers("Madrid", "audífonos")
        print(f"✅ Encontrados {centers.get('total_results', 0)} centros")
        print(f"📡 Fuente: {centers.get('source', 'N/A')}")
        
        if centers.get('centers'):
            for i, center in enumerate(centers['centers'][:3], 1):
                print(f"   {i}. {center.get('name', 'N/A')}")
                print(f"      📍 {center.get('address', 'N/A')}")
                if center.get('phone'):
                    print(f"      📞 {center.get('phone')}")
                print()
    except Exception as e:
        print(f"❌ Error en búsqueda de centros: {e}")
    
    # 2. Probar noticias médicas
    print("2️⃣ Búsqueda de noticias médicas:")
    try:
        news = medical_news_provider.get_latest_hearing_aid_news(days=30)
        print(f"✅ Encontradas {news.get('total_results', 0)} noticias")
        print(f"📡 Fuente: {news.get('source', 'N/A')}")
        
        if news.get('articles'):
            for i, article in enumerate(news['articles'][:2], 1):
                print(f"   {i}. {article.get('title', 'N/A')}")
                print(f"      📝 {article.get('description', 'N/A')[:80]}...")
                print()
    except Exception as e:
        print(f"❌ Error en búsqueda de noticias: {e}")
    
    # 3. Probar consejos médicos
    print("3️⃣ Consejos médicos por tema:")
    topics = ["mantenimiento", "precios", "tecnología", "adaptación"]
    for topic in topics:
        try:
            advice = medical_news_provider.get_medical_advice_by_topic(topic)
            print(f"💡 {topic.upper()}:")
            print(f"   {advice[:100]}...")
            print()
        except Exception as e:
            print(f"❌ Error en consejo de {topic}: {e}")
    
    # 4. Probar tendencias médicas
    print("4️⃣ Tendencias actuales:")
    try:
        trends = medical_news_provider.get_medical_trends()
        print(trends)
        print()
    except Exception as e:
        print(f"❌ Error en tendencias: {e}")

def test_chatbot_node():
    """Prueba el nodo del chatbot con búsqueda web"""
    
    print("🤖 Probando nodo del chatbot con búsqueda web...\n")
    
    # Crear instancia del nodo
    nodes = ChatbotNodes()
    
    # Ejemplos de consultas para hearing_aids_node
    hearing_queries = [
        "Busco centros de audífonos en Barcelona",
        "¿Cuánto cuestan los audífonos?",
        "Consejos para mantener mis audífonos",
        "¿Qué tecnología tienen los audífonos modernos?",
        "Noticias sobre audífonos"
    ]
    
    print("🎧 Probando hearing_aids_node:")
    for i, query in enumerate(hearing_queries, 1):
        print(f"📝 Consulta {i}: {query}")
        
        # Simular estado del chatbot
        state = {
            "user_input": query,
            "text_generator_model": "gemini",
            "messages": [],
            "conversation_history": []
        }
        
        try:
            # Ejecutar el nodo
            result = nodes.hearing_aids_node(state)
            
            if "response" in result:
                print(f"✅ Respuesta: {result['response'][:200]}...")
            else:
                print("❌ No se generó respuesta")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)
    
    # Ejemplos de consultas para medical_center_node
    medical_queries = [
        "Busco especialistas en otorrinolaringología en Madrid",
        "¿Dónde hay hospitales con especialistas en audición?",
        "Necesito una clínica para revisión auditiva en Valencia",
        "¿Hay urgencias para problemas de audición?",
        "Quiero programar una cita con un audiólogo"
    ]
    
    print("\n🏥 Probando medical_center_node:")
    for i, query in enumerate(medical_queries, 1):
        print(f"📝 Consulta {i}: {query}")
        
        # Simular estado del chatbot
        state = {
            "user_input": query,
            "text_generator_model": "gemini",
            "messages": [],
            "conversation_history": []
        }
        
        try:
            # Ejecutar el nodo
            result = nodes.medical_center_node(state)
            
            if "response" in result:
                print(f"✅ Respuesta: {result['response'][:200]}...")
            else:
                print("❌ No se generó respuesta")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de búsqueda web en tiempo real\n")
    
    # Ejecutar pruebas
    test_web_search_functionality()
    test_chatbot_node()
    
    print("✅ Pruebas completadas!") 