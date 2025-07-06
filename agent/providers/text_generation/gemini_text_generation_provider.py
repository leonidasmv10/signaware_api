from .text_generation_provider import TextGenerationProvider
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class GeminiTextGenerationProvider(TextGenerationProvider):
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def execute(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text 