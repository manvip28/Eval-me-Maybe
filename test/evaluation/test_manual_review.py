import pytest
from unittest.mock import patch, MagicMock
from src.evaluation.manual_review import review_questions
import json

@pytest.fixture
def sample_questions(tmp_path):
    data = [
        {
            "question": "What is EC2?",
            "bloom": "Remember",
            "marks": 1,
            "source_topic": "1.1 Cloud Basics",
            "keywords_used": ["EC2"],
            "approved": False,
            "feedback": None
        }
    ]
    file_path = tmp_path / "questions.json"
    with open(file_path, 'w') as f:
        json.dump(data, f)
    return file_path

def test_review_process(sample_questions, monkeypatch):
    # Simulate user approving the question
    monkeypatch.setattr('builtins.input', lambda _: "A")
    
    with patch('src.evaluation.manual_review.display') as mock_display:
        review_questions(sample_questions)
    
    # Verify question was approved
    with open(sample_questions) as f:
        updated = json.load(f)
        assert updated[0]['approved'] is True

def test_feedback_capture(sample_questions, monkeypatch):
    # Simulate user providing feedback
    responses = iter(["E", "Too vague", "S"])
    monkeypatch.setattr('builtins.input', lambda _: next(responses))
    
    review_questions(sample_questions)
    
    with open(sample_questions) as f:
        updated = json.load(f)
        assert updated[0]['feedback'] == "Too vague"
        assert updated[0]['approved'] is False

def test_batch_processing(sample_questions, monkeypatch):
    # Simulate processing multiple questions
    monkeypatch.setattr('builtins.input', lambda _: "A")
    
    with patch('src.evaluation.manual_review.display') as mock_display:
        # Add multiple questions to the file
        with open(sample_questions, 'r+') as f:
            data = json.load(f)
            data.append({
                "question": "Explain S3 architecture",
                "bloom": "Understand",
                "marks": 5,
                "approved": False
            })
            f.seek(0)
            json.dump(data, f)
        
        review_questions(sample_questions)
    
    with open(sample_questions) as f:
        updated = json.load(f)
        assert all(q['approved'] for q in updated)