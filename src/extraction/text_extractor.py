import re

def is_topic_header(text: str) -> bool:
    """Detect if text is a topic header"""
    patterns = [
        r"^\d+\.\d+\s+[A-Z]",  # 1.1 TITLE
        r"^Chapter\s+\d+:",     # Chapter 1:
        r"^[A-Z]{3,}\s*$",      # ALL CAPS HEADERS
        r"^\d+\.\s+[A-Z]",       # 1. TITLE
        r"^\d+\s+[A-Z]"         # 1 TITLE
    ]
    return any(re.match(p, text.strip()) for p in patterns)

def clean_header(header: str) -> str:
    """Clean and normalize section headers"""
    # Remove numbering prefixes (e.g., "1.1. ")
    header = re.sub(r"^(?:\d+\.)+\s*", "", header)
    
    # Remove trailing punctuation
    header = header.strip(" :.-")
    
    # Title case normalization
    return " ".join(word.capitalize() for word in header.split())