import PyPDF2
import fitz  # PyMuPDF
import os
from typing import Optional, List

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file using multiple methods.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF file
    """
    print(f"DEBUG PDF_UTILS: Attempting to read PDF: {file_path}")
    print(f"DEBUG PDF_UTILS: File exists: {os.path.exists(file_path)}")
    
    # Try PyMuPDF first (better for complex PDFs)
    text = ""
    try:
        pdf_doc = fitz.open(file_path)
        print(f"DEBUG PDF_UTILS: PyMuPDF - PDF has {len(pdf_doc)} pages")
        
        for page_num in range(len(pdf_doc)):
            page = pdf_doc.load_page(page_num)
            page_text = page.get_text()
            print(f"DEBUG PDF_UTILS: PyMuPDF - Page {page_num+1} text length: {len(page_text)}")
            text += page_text
        
        pdf_doc.close()
        print(f"DEBUG PDF_UTILS: PyMuPDF - Total extracted text length: {len(text)}")
        
        if text.strip():
            return text
        else:
            print("DEBUG PDF_UTILS: PyMuPDF extracted no text, trying PyPDF2...")
    except Exception as e:
        print(f"ERROR PDF_UTILS: PyMuPDF failed: {e}")
    
    # Fallback to PyPDF2
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            print(f"DEBUG PDF_UTILS: PyPDF2 - PDF has {len(reader.pages)} pages")
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                print(f"DEBUG PDF_UTILS: PyPDF2 - Page {i+1} text length: {len(page_text)}")
                text += page_text
    except Exception as e:
        print(f"ERROR PDF_UTILS: PyPDF2 also failed: {e}")
        return ""
    
    print(f"DEBUG PDF_UTILS: PyPDF2 - Total extracted text length: {len(text)}")
    return text
