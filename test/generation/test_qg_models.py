import pytest
from unittest.mock import patch, MagicMock
from src.generation.qg_models import QGModel

@pytest.fixture
def mock_model():
    with patch('transformers.pipeline') as mock_pipe:
        mock_model = QGModel()
        mock_model.pipe = MagicMock()
        mock_model.pipe.return_value = [{"generated_text": "Sample question about cloud computing"}]
        return mock_model

def test_question_generation(mock_model):
    prompt = "Generate a question about AWS"
    result = mock_model.generate(prompt)
    
    assert "question" in result
    assert "cloud computing" in result
    mock_model.pipe.assert_called_once_with(
        prompt, 
        max_new_tokens=250,
        do_sample=True,
        temperature=0.7
    )

def test_quantization_config():
    model = QGModel()
    assert hasattr(model.model, "quantization_config")
    config = model.model.quantization_config
    assert config.load_in_4bit is True
    assert config.bnb_4bit_quant_type == "nf4"
    assert config.bnb_4bit_compute_dtype == "torch.bfloat16"

@patch('transformers.AutoModelForCausalLM.from_pretrained')
def test_model_loading(mock_from_pretrained):
    QGModel(model_name="mistralai/Mistral-7B-Instruct-v0.1")
    mock_from_pretrained.assert_called_once_with(
        "mistralai/Mistral-7B-Instruct-v0.1",
        load_in_4bit=True,
        device_map="auto"
    )