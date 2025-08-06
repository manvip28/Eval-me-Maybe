from keybert import KeyBERT
import spacy
from typing import List, Dict

class KeywordExtractor:
    def __init__(self, model_name="all-MiniLM-L6-v2", spacy_model="en_core_web_sm"):
        self.bert_model = KeyBERT(model_name)
        self.nlp = spacy.load(spacy_model)
        
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """Extract keywords using KeyBERT with spaCy filtering"""
        # First pass with KeyBERT
        keywords = self.bert_model.extract_keywords(
            text, 
            keyphrase_ngram_range=(1, 2),
            stop_words="english",
            top_n=top_n * 2  # Get extra for filtering
        )
        
        # Filter with spaCy for nouns/noun phrases
        doc = self.nlp(text)
        valid_pos = {"NOUN", "PROPN"}
        filtered_keywords = []
        
        for kw, score in keywords:
            # Check if keyword contains meaningful nouns
            tokens = [token for token in self.nlp(kw) if token.pos_ in valid_pos]
            if tokens and any(token.text.lower() not in self.nlp.Defaults.stop_words for token in tokens):
                filtered_keywords.append(kw)
                
        return filtered_keywords[:top_n]
    
    def process_topics(self, topics: Dict[str, str]) -> Dict[str, List[str]]:
        """Process a dictionary of topics to extract keywords for each"""
        return {topic: self.extract_keywords(content) for topic, content in topics.items()}