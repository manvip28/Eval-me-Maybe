# src/evaluation/manual_review.py
import json

def review_questions(question_file):
    with open(question_file) as f:
        questions = json.load(f)
    
    for q in questions:
        print((f"**{q['bloom']} ({q['marks']} marks)**"))
        print((q['question']))
        print((f"*Keywords: {', '.join(q['keywords_used'])}*"))
        
        action = input("[A]pprove [R]eject [E]dit: ").upper()
        if action == "A":
            q['approved'] = True
        elif action == "E":
            q['feedback'] = input("Feedback: ")
        # ... save updated status