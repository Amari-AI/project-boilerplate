import PyPDF2
import base64
from typing import List, Tuple
import io

def extract_text_from_pdf(file_path: str) -> Tuple[str, List[str]]:
    """
    Extract text from a PDF file using PyPDF2.
    Returns both extracted text and base64 encoded images if text extraction fails.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Tuple[str, List[str]]: Extracted text and list of base64 encoded images
    """
    text = ""
    images = []
    
    # Extract text using PyPDF2
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text.strip():
                    text += page_text + "\n"
    except Exception as e:
        print(f"PyPDF2 extraction failed: {e}")
    
    # If no meaningful text found (empty or very short), extract images for vision model
    if not text.strip() or len(text.strip()) < 10:
        print("No meaningful text found in PDF, extracting images for vision model...")
        images = extract_images_from_pdf(file_path)
        return "", images
    
    return text.strip(), []

def extract_images_from_pdf(file_path: str, max_images: int = 5) -> List[str]:
    """
    Convert PDF pages to images and encode as base64 for vision model processing.
    
    Args:
        file_path: Path to the PDF file
        max_images: Maximum number of images to extract
        
    Returns:
        List[str]: List of base64 encoded images
    """
    images = []
    
    try:
        from pdf2image import convert_from_path
        from PIL import Image
        
        # Convert PDF pages to images
        pages = convert_from_path(file_path, first_page=1, last_page=max_images)
        
        for i, page in enumerate(pages):
            if i >= max_images:
                break
                
            # Convert PIL image to base64
            buffer = io.BytesIO()
            page.save(buffer, format='PNG')
            img_data = buffer.getvalue()
            
            # Convert to base64
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            images.append(img_base64)
        
    except ImportError:
        print("pdf2image not available. Install with: pip install pdf2image")
        print("Also ensure poppler is installed on your system")
    except Exception as e:
        print(f"Error extracting images from PDF: {e}")
    
    return images
