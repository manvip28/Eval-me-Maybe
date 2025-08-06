import pytest
from src.generation.bloom_mapper import get_chunk
import tiktoken

#@pytest.fixture
def sample_content():
    return ("This is a sample text about cloud computing. " * 100)

def test_chunk_sizing(sample_content):
    # Test Remember level
    chunk = get_chunk(sample_content, "remember", 1)
    tokens = len(tiktoken.get_encoding("cl100k_base").encode(chunk))
    assert tokens <= 150  # 300 * (1/2) since max mark=2
    
    # Test Understand level with high marks
    chunk = get_chunk(sample_content, "understand", 10)
    tokens = len(tiktoken.get_encoding("cl100k_base").encode(chunk))
    assert tokens > 500 and tokens <= 600
    
    # Test Create level should return full content
    full_chunk = get_chunk(sample_content, "create", 10)
    assert full_chunk == sample_content

def test_edge_cases():
    # Empty content
    assert get_chunk("", "remember", 1) == ""
    
    # Invalid bloom level
    with pytest.raises(KeyError):
        get_chunk("content", "InvalidLevel", 5)
    
    # Marks outside range
    with pytest.raises(ValueError):
        get_chunk("content", "remember", 0)
    with pytest.raises(ValueError):
        get_chunk("content", "remember", 3)

test_chunk_sizing(sample_content())
print("hello")