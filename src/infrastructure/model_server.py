from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from .quantization import get_quantization_config
import torch

app = FastAPI()

class GenerationRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 250
    temperature: float = 0.7

# Load model on startup
@app.on_event("startup")
async def load_model():
    global generator
    quant_config = get_quantization_config()
    model_name = "mistralai/Mistral-7B-Instruct-v0.2"
    
    generator = pipeline(
        "text-generation",
        model=model_name,
        device_map="auto",
        model_kwargs={
            "quantization_config": quant_config,
            "torch_dtype": torch.bfloat16
        }
    )

@app.post("/generate")
async def generate_text(request: GenerationRequest):
    response = generator(
        request.prompt,
        max_new_tokens=request.max_new_tokens,
        temperature=request.temperature,
        do_sample=True
    )
    return {"generated_text": response[0]['generated_text']}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": "Mistral-7B"}