from .text_generation_provider import TextGenerationProvider
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
import torch
import os

class LeonidasmvTextGenerationProvider(TextGenerationProvider):
    def __init__(self):
        model_name = "leonidasmv/mistral-7b-instruct-v0.3-auditory-assistant-finetuning"
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True,
        )
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=bnb_config,
                device_map="auto",
                torch_dtype="auto"
            )
        except Exception as e:
            print(f"Could not load with quantization: {e}")
            print("Attempting to load the model normally. This may require more VRAM.")
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto"
            )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        )

    def execute(self, prompt):
        # prompt: string (user message)
        messages = [
            {"role": "user", "content": prompt}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        generated_text = self.generator(
            text,
            max_new_tokens=250,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
            repetition_penalty=1.1,
            pad_token_id=self.tokenizer.eos_token_id,
            eos_token_id=self.tokenizer.eos_token_id
        )
        response_only = generated_text[0]['generated_text'].replace(text, "").strip()
        return response_only 