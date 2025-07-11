from .text_generation_provider import TextGenerationProvider
from openai import OpenAI
import os

class OpenAITextGenerationProvider(TextGenerationProvider):
    def __init__(self, model_name="gpt-3.5-turbo"):
        self.model_name = model_name
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def execute(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.7,
        )
        return response.choices[0].message.content 