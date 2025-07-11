from typing import TypedDict, Annotated, List, Optional
import operator
from langchain_core.messages import BaseMessage


class ChatbotState(TypedDict):
    # Campos para el chatbot
    messages: Annotated[List[BaseMessage], operator.add]
    user_input: str
    detected_intent: str
    response: str
    conversation_history: List[dict]
    text_generator_model: str  # Generador de texto a usar (gemini, openai, etc.)
