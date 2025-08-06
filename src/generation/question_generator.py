# import yaml
# from jinja2 import Template
# from .bloom_mapper import get_chunk
# from .qg_models import QGModel
# import random
# from typing import Dict, List
# from .bloom_config import BLOOM_CONFIG
# class QuestionGenerator:
#     def __init__(self, 
#                  bloom_config_path="src/generation/bloom_config.yaml",
#                  prompt_path="src/generation/prompt_engine/prompts.yaml"):
#         # Load configuration
#         self.bloom_config = BLOOM_CONFIG
        
#         with open(prompt_path) as f:
#             self.prompt_templates = yaml.safe_load(f)
        
#         self.qg_model = QGModel()
    
#     def select_bloom_level(self, topic_length: int) -> str:
#         """Select Bloom's level based on topic complexity"""
#         if topic_length < 500:
#             return "Remember"
#         elif topic_length < 1500:
#             return random.choice(["Remember", "Understand", "Apply"])
#         else:
#             weights = [1, 2, 3, 4, 2, 1]  # Higher weight for Apply/Analyze
#             return random.choices(
#                 list(self.bloom_config.keys()),
#                 weights=weights,
#                 k=1
#             )[0]
    
#     def generate_question(self, topic: str, content: str, keywords: List[str]) -> Dict:
#         """Generate a single question for a topic"""
#         # Select Bloom level
#         bloom_level = self.select_bloom_level(len(content))
        
#         # Select marks based on Bloom config
#         possible_marks = self.bloom_config[bloom_level]["marks"]
#         marks = random.choice(possible_marks)
        
#         # Get content chunk
#         chunk = get_chunk(content, bloom_level, marks)
        
#         # Get prompt template
#         template_str = self.prompt_templates[bloom_level].get(str(marks))
#         if not template_str:
#             # Fallback to highest available marks template
#             max_mark = max([int(m) for m in self.prompt_templates[bloom_level].keys()])
#             template_str = self.prompt_templates[bloom_level][max_mark]
        
#         # Render prompt
#         template = Template(template_str)
#         if len(chunk)>1024:
#             chunk = chunk[:1024]
#         prompt = template.render(
#             marks=marks,
#             bloom=bloom_level,
#             chunk=chunk,
#             keywords=keywords
#         )
        
#         # Generate question
#         question_text = self.qg_model.generate(prompt)
        
#         # Clean and format
#         question_text = question_text.strip()
#         if "Question:" in question_text:
#             question_text = question_text.split("Question:")[-1].strip()
        
#         # Select keywords used (at least 2 if possible)
#         num_keywords = min(2, len(keywords)) if marks < 5 else min(3, len(keywords))
#         used_keywords = random.sample(keywords, num_keywords)
        
#         return {
#             "question": question_text,
#             "bloom": bloom_level,
#             "marks": marks,
#             "source_topic": topic,
#             "keywords_used": used_keywords,
#             "approved": False,
#             "feedback": None
#         }
    
#     def generate_for_topics(self, topics: Dict[str, str], 
#                            keywords_dict: Dict[str, List[str]],
#                            questions_per_topic: int = 3) -> List[Dict]:
#         """Generate questions for multiple topics"""
#         questions = []
#         for topic, content in topics.items():
#             keywords = keywords_dict.get(topic, [])
#             for _ in range(questions_per_topic):
#                 questions.append(self.generate_question(topic, content, keywords))
#         return questions
import requests
import random
from jinja2 import Template
from typing import Dict, List
from .bloom_mapper import get_chunk
from .bloom_config import BLOOM_CONFIG

class QuestionGenerator:
    def __init__(self, 
                 prompt_path: str = "src/generation/prompt_engine/prompts.yaml",
                 api_key: str = "XXXX",  # Replace with your OpenRouter key
                 model: str = "mistralai/mistral-7b-instruct"):
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://yourdomain.com",
            "Content-Type": "application/json"
        }
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

        with open(prompt_path) as f:
            import yaml
            self.prompt_templates = yaml.safe_load(f)

        self.bloom_config = BLOOM_CONFIG

    def _call_openrouter(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that creates academic questions."},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            res = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)

            if res.status_code != 200:
                print("❌ OpenRouter Error Response:")
                print(res.status_code, res.text)
                raise Exception(f"OpenRouter error: {res.status_code}")

            data = res.json()
            return data["choices"][0]["message"]["content"].strip()

        except requests.exceptions.JSONDecodeError:
            print("❌ Failed to decode JSON. Raw response:")
            print(res.text)
            raise Exception("OpenRouter response was not valid JSON.")

        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            raise


    def generate_question(self, topic: str, content: str, keywords: List[str]) -> Dict:
        bloom_level = self.select_bloom_level(len(content))
        possible_marks = self.bloom_config[bloom_level]["marks"]
        marks = random.choice(possible_marks)
        chunk = get_chunk(content, bloom_level, marks)

        # Prompt template render
        template_str = self.prompt_templates[bloom_level].get(str(marks))
        if not template_str:
            template_str = self.prompt_templates[bloom_level][max(map(int, self.prompt_templates[bloom_level].keys()))]

        prompt = Template(template_str).render(
            marks=marks,
            bloom=bloom_level,
            chunk=chunk,
            keywords=keywords
        )

        question_text = self._call_openrouter(prompt)
        question_text = self._clean_question(question_text)

        used_keywords = random.sample(keywords, min(len(keywords), 2 if marks < 5 else 3))

        return {
            "question": question_text,
            "bloom": bloom_level,
            "marks": marks,
            "source_topic": topic,
            "keywords_used": used_keywords,
            "chunk":chunk,
            "approved": True,
            "feedback": None
        }

    def _clean_question(self, text: str) -> str:
        text = text.strip()
        if "Question:" in text:
            text = text.split("Question:")[-1].strip()
        return text.split("\n")[0]

    def select_bloom_level(self, topic_length: int) -> str:
        if topic_length < 500:
            return "Remember"
        elif topic_length < 1500:
            return random.choice(["Remember", "Understand", "Apply"])
        else:
            weights = [1, 2, 3, 4, 2, 1]
            return random.choices(list(self.bloom_config.keys()), weights=weights, k=1)[0]

    def generate_for_topics(self, topics: Dict[str, str], keywords_dict: Dict[str, List[str]], questions_per_topic: int = 3) -> List[Dict]:
        questions = []
        for topic, content in topics.items():
            keywords = keywords_dict.get(topic, [])
            for _ in range(questions_per_topic):
                questions.append(self.generate_question(topic, content, keywords))
        return questions
