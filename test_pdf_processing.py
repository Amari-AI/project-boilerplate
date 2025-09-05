#!/usr/bin/env python3

# Test script to demonstrate PDF processing works
import sys
import os
sys.path.append('.')

from app.utils.pdf_utils import extract_text_from_pdf
from app.services.llm_service import extract_field_from_document

def test_pdf_processing():
    print("=== PDF Processing Test ===")
    
    # Check if we have any PDF files to test with
    test_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.lower().endswith('.pdf'):
                test_files.append(os.path.join(root, file))
                if len(test_files) >= 1:  # Just test one file
                    break
        if test_files:
            break
    
    if not test_files:
        print("No PDF files found for testing.")
        print("Please provide a PDF file path to test with:")
        pdf_path = input("PDF file path: ").strip('"')
        if not os.path.exists(pdf_path):
            print(f"File not found: {pdf_path}")
            return
        test_files = [pdf_path]
    
    for pdf_path in test_files:
        print(f"\n--- Testing PDF: {pdf_path} ---")
        print(f"File exists: {os.path.exists(pdf_path)}")
        print(f"File size: {os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 'N/A'} bytes")
        
        # Test text extraction
        text = extract_text_from_pdf(pdf_path)
        print(f"Extracted text length: {len(text)} characters")
        print(f"Text sample: {text[:300]}...")
        
        if text.strip():
            # Test LLM processing
            document_data = {'combined_text': f"Document: {os.path.basename(pdf_path)}\n{text}"}
            result = extract_field_from_document(document_data)
            print(f"\nLLM processing result:")
            print(f"Status: {result.get('status')}")
            if 'structured_data' in result:
                print(f"Document type: {result['structured_data'].get('document_type')}")
                print(f"Fields found: {list(result['structured_data'].get('extracted_fields', {}).keys())}")
        else:
            print("No text extracted from PDF")

if __name__ == "__main__":
    test_pdf_processing()