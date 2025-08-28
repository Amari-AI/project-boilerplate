import PyPDF2
import fitz  # PyMuPDF
import base64
import os
from typing import Optional, List, Dict, Any

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file. If text extraction fails,
    extract as image for visual processing.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF file or a marker for image-based PDF
    """
    try:
        # First try with PyPDF2
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if text.strip():
                return text
        
        # If no text, try with PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text += page_text + "\n"
        
        if text.strip():
            return text
        
        # If still no text, it's likely an image-based PDF
        # Return a marker that tells the system to process it as an image
        return "[IMAGE_PDF: This PDF contains embedded images instead of text. Visual processing required.]"
        
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def extract_pdf_as_image_data(file_path: str) -> Dict[str, Any]:
    """
    Extract PDF pages as images for visual processing.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        dict: Contains image data and metadata
    """
    try:
        doc = fitz.open(file_path)
        images = []
        
        for page_num, page in enumerate(doc):
            # Render page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            img_data = pix.tobytes("png")
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            images.append({
                'page': page_num + 1,
                'image_base64': img_base64,
                'width': pix.width,
                'height': pix.height
            })
        
        doc.close()
        
        return {
            'total_pages': len(images),
            'images': images,
            'is_image_pdf': True
        }
        
    except Exception as e:
        return {'error': str(e)}