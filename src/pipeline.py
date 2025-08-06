import json
import time
from .extraction.pdf_extractor import extract_topics
from .knowledge.keyword_extractor import KeywordExtractor
from .generation.question_generator import QuestionGenerator
from .evaluation.manual_review import review_questions
from .generation.context_generator import ContentGenerator
def run_pipeline(input_path: str, output_file: str = "generated_questions.json"):
    """Main pipeline execution"""
    print("🚀 Starting textbook processing pipeline")
    
    # 1. Text Extraction
    print("📖 Extracting topics from textbook...")
    start = time.time()
    topics = extract_topics(input_path)
    print(f"✅ Extracted {len(topics)} topics in {time.time()-start:.1f}s")
    
    # 2. Keyword Extraction
    print("🔑 Extracting keywords...")
    keyword_extractor = KeywordExtractor()
    start = time.time()
    keywords_dict = keyword_extractor.process_topics(topics)
    print(f"✅ Extracted keywords in {time.time()-start:.1f}s")
    
    # 3. Question Generation
    print("❓ Generating questions...")
    qg = QuestionGenerator(api_key="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")
    start = time.time()
    questions = qg.generate_for_topics(topics, keywords_dict)
    print(f"✅ Generated {len(questions)} questions in {time.time()-start:.1f}s")
    
    # 4. Save intermediate results
    with open(output_file, "w") as f:
        json.dump(questions, f, indent=2)
    print(f"💾 Saved questions to {output_file}")
    
    # 5. Manual Review
    print("\n👨‍🏫 Starting manual review process...")
    review_questions(output_file)

    # print("✅ Manual review completed. Generating Answer...  ")
    # ag= ContentGenerator(api_key="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",questions=questions)
    # answers = ag.generate_review_materials(questions, style="study_guide")

    # print("✅ Answers generated successfully. Saving to file...")
    # with open("reviewed_questions.json", "w") as f:
    #     json.dump(answers, f, indent=2)
    print("\n🎉 Pipeline completed! Approved questions are ready for use.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <textbook_path.pdf> [output_file.json]")
        sys.exit(1)
    
    output_file = sys.argv[2] if len(sys.argv) > 2 else "generated_questions.json"
    run_pipeline(sys.argv[1], output_file)