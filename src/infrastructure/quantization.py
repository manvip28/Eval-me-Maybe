from transformers import BitsAndBytesConfig
import torch

def get_quantization_config() -> BitsAndBytesConfig:
    """Get 4-bit quantization configuration for efficient inference"""
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True
    )

def optimize_model(model):
    """Apply optimization techniques to model"""
    # Freeze base layers
    for param in model.base_model.parameters():
        param.requires_grad = False
        
    # Enable gradient checkpointing
    if hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()
        
    # Prepare model for k-bit training
    model = prepare_model_for_kbit_training(model)
    return model