# src/generation/qg_models.py
from transformers import pipeline, AutoModelForCausalLM,AutoTokenizer

class QGModel:
    def __init__(self, model_name="TheBloke/Mistral-7B-Instruct-v0.1-GGUF"):
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto",
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.pipe = pipeline("text-generation", model=self.model,tokenizer=tokenizer)

    def generate(self, prompt, max_new_tokens=250):
        return self.pipe(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7
        )[0]['generated_text']