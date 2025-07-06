from agent.providers.text_generation.gemini_text_generation_provider import (
    GeminiTextGenerationProvider,
)
from agent.services.intention_classifier_service import (
    IntentionClassifierService,
)
from agent.workflow import create_workflow, get_initial_state


class SoundDetectorAgent:
    def __init__(self):
        self.text_generation_provider = GeminiTextGenerationProvider()
        self.intention_classifier_service = IntentionClassifierService()

        workflow_graph = create_workflow()
        self.compiled_workflow = workflow_graph.compile()
        self.initial_state = get_initial_state()

    def execute(self, user_input, audio_path, audio_file):
        try:

            self.initial_state["audio_path"] = audio_path
            self.initial_state["audio_file"] = audio_file

            final_state = self.compiled_workflow.invoke(self.initial_state)
            return final_state.get("sound_type", "Unknown")
        except Exception as e:
            print(f"❌ Error al clasificar intención: {e}")
            return "GENERAL_QUERY"
