#!/usr/bin/env python3
"""
Main execution script for Textbook to Questions pipeline
"""
import argparse
from src.pipeline import run_pipeline
from src.infrastructure.azure_utils import AzureStorage

def main():
    parser = argparse.ArgumentParser(description="AI-Powered Exam Question Generator")
    parser.add_argument("input", help="Path to textbook PDF or text file")
    parser.add_argument("-o", "--output", default="questions.json", 
                        help="Output JSON file for questions")
    parser.add_argument("--upload", action="store_true", 
                        help="Upload results to Azure Blob Storage")
    parser.add_argument("--review", action="store_true", 
                        help="Run manual review after generation")
    
    args = parser.parse_args()
    
    # Run main pipeline
    run_pipeline(args.input, args.output)
    
    # Optional Azure upload
    if args.upload:
        azure = AzureStorage(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
        url = azure.upload_file(args.output, "question-bank", args.output)
        print(f"📤 Uploaded to Azure: {url}")
    
    # Run review if requested
    if args.review:
        from src.evaluation.manual_review import review_questions
        review_questions(args.output)

if __name__ == "__main__":
    main()