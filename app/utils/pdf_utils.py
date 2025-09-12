import PyPDF2
import os
import base64
from typing import Optional, List

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file. First try PyPDF2, if that fails 
    (for scanned PDFs), return the file as base64 for Claude vision processing.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF file, or base64 data if text extraction fails
    """
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                text += page_text
        
        # If we got meaningful text, return it
        if text.strip():
            return text
        else:
            # If no text extracted, this might be a scanned PDF
            # Return a marker that indicates we need vision processing
            return f"<SCANNED_PDF:{file_path}>"
            
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {str(e)}")
        return ""

def get_pdf_as_base64(file_path: str) -> str:
    """
    Convert PDF to base64 for Claude vision processing.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        str: Base64 encoded PDF
    """
    try:
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error converting PDF to base64 {file_path}: {str(e)}")
        return ""
