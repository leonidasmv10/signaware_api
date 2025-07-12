"""
Script para probar que el workflow funciona correctamente después del fix del método async.
"""

import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.workflows.chatbot_worklow import ChatbotWorkflow

def test_workflow():
    """Prueba que el workflow funciona correctamente."""
    print("🧪 Probando workflow después del fix...")
    
    try:
        # Crear instancia del workflow
        workflow = ChatbotWorkflow()
        
        print("✅ Workflow creado correctamente")
        
        # Crear estado inicial
        initial_state = workflow.get_initial_state()
        initial_state["user_input"] = "Quiero información sobre el Virto Infinio"
        
        print(f"📝 Estado inicial creado con input: '{initial_state['user_input']}'")
        
        # Ejecutar workflow
        print("🔄 Ejecutando workflow...")
        final_state = workflow.execute(initial_state)
        
        print("✅ Workflow ejecutado correctamente")
        print(f"📊 Estado final:")
        print(f"   Intención detectada: {final_state.get('detected_intent', 'N/A')}")
        print(f"   Respuesta: {final_state.get('response', 'N/A')[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en workflow: {e}")
        return False

def test_hearing_aids_node_directly():
    """Prueba el nodo de audífonos directamente."""
    print("\n🧪 Probando nodo de audífonos directamente...")
    
    try:
        from agent.nodes.chatbot_nodes import ChatbotNodes
        
        # Crear instancia de nodos
        nodes = ChatbotNodes()
        
        # Crear estado de prueba
        test_state = {
            "user_input": "Quiero información sobre el Virto Infinio",
            "text_generator_model": "gemini"
        }
        
        print(f"📝 Probando con input: '{test_state['user_input']}'")
        
        # Ejecutar nodo
        final_state = nodes.hearing_aids_node(test_state)
        
        print("✅ Nodo ejecutado correctamente")
        print(f"📝 Respuesta: {final_state.get('response', 'N/A')[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en nodo: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del workflow...")
    
    # Probar workflow completo
    workflow_ok = test_workflow()
    
    # Probar nodo directamente
    node_ok = test_hearing_aids_node_directly()
    
    print(f"\n{'='*50}")
    if workflow_ok and node_ok:
        print("✅ Todas las pruebas pasaron correctamente")
    else:
        print("❌ Algunas pruebas fallaron")
    print(f"{'='*50}") 