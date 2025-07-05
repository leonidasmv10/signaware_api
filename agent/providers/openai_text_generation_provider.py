from .text_generation_provider import TextGenerationProvider
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

class OpenAITextGenerationProvider(TextGenerationProvider):
    def __init__(self, model_name="gpt-3.5-turbo"):
        self.model_name = model_name

    def generate(self, prompt):
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.7,
        )
        return response.choices[0].message["content"] 