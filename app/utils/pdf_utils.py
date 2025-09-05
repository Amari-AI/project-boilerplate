import logging
import os
import shutil
import tempfile
from typing import Optional, List

from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from app.core.config import settings

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF file
    """
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = PdfReader(file)
            for page in reader.pages:
                # extract_text can return None if no text is found on the page
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    except Exception:
        # In case of any parsing errors, fall back to empty text
        return ""
    return text.strip()


def ocr_text_from_pdf(file_path: str) -> str:
    """
    Convert PDF pages to PNG and run Tesseract OCR to extract text.
    Saves PNGs into a temporary directory for debugging and cleans them up
    unless OCR_KEEP_IMAGES is true.
    """
    if not settings.OCR_ENABLED:
        return ""

    temp_dir = tempfile.mkdtemp(prefix="ocr_")
    images: List[Image.Image] = []
    ocr_text_parts: List[str] = []
    try:
        logger.info("Starting OCR conversion for '%s' at %sdpi into '%s'", file_path, settings.OCR_DPI, temp_dir)
        images = convert_from_path(file_path, dpi=settings.OCR_DPI)
        logger.info("Converted %d pages to images for OCR", len(images))
        for idx, img in enumerate(images, start=1):
            out_path = os.path.join(temp_dir, f"page_{idx:04d}.png")
            img.save(out_path, format="PNG")
            try:
                txt = pytesseract.image_to_string(Image.open(out_path))
            except Exception as e:
                logger.warning("Tesseract failed on %s: %s", out_path, e)
                txt = ""
            if txt and txt.strip():
                ocr_text_parts.append(txt.strip())
    except Exception as e:
        logger.exception("OCR pipeline failed for '%s': %s", file_path, e)
        return ""
    finally:
        if settings.OCR_KEEP_IMAGES:
            logger.info("Keeping OCR images in '%s' for inspection", temp_dir)
        else:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info("Removed OCR temp dir '%s'", temp_dir)
            except Exception as cleanup_err:
                logger.warning("Failed to remove OCR temp dir '%s': %s", temp_dir, cleanup_err)

    return "\n".join(ocr_text_parts).strip()
