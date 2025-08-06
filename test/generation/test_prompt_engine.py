import pytest
from src.generation.prompt_engine.jinja_render import render_prompt
import yaml

# Sample prompt template
SAMPLE_PROMPT = """
Generate a {{marks}}-mark {{bloom}}-level question about:
{{keywords|join(', ')}}

Context:
{{chunk}}
"""

def test_prompt_rendering():
    context = {
        "marks": 10,
        "bloom": "Understand",
        "keywords": ["EC2", "S3", "Scalability"],
        "chunk": "Amazon EC2 provides virtual servers..."
    }
    
    result = render_prompt(SAMPLE_PROMPT, context)
    
    assert "10-mark" in result
    assert "Understand-level" in result
    assert "EC2, S3, Scalability" in result
    assert "virtual servers" in result

def test_yaml_loading():
    with open("src/generation/prompt_engine/prompts.yaml") as f:
        prompts = yaml.safe_load(f)
        
    assert "Remember" in prompts
    assert "Understand" in prompts
    assert "10" in prompts["Understand"]
    assert "{{keywords}}" in prompts["Remember"]["1"]

def test_edge_cases():
    # Missing variable
    with pytest.raises(Exception):
        render_prompt("Hello {{name}}", {})
    
    # Empty template
    assert render_prompt("", {"a":1}) == ""