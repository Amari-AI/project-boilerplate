import os
from typing import Optional

import PyPDF2
from pdf2image import convert_from_path
import pytesseract


def extract_text_from_pdf(
    file_path: str, password: Optional[str] = None, use_ocr: bool = True
) -> str:
    """
    Extract text from a PDF file, with OCR fallback if needed.

    Args:
        file_path: Path to the PDF file
        password: Optional password for encrypted PDFs
        use_ocr: Whether to use OCR fallback if no text is found

    Returns:
        str: Extracted text from the PDF file
    """
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)

            if reader.is_encrypted:
                if password:
                    reader.decrypt(password)
                else:
                    print("ERROR: PDF is encrypted. Provide a password.")
                    return ""

            print(f"DEBUG: PDF has {len(reader.pages)} pages")

            for page_num, page in enumerate(reader.pages):
                page_text = ""
                try:
                    page_text = page.extract_text()
                except Exception as e:
                    print(
                        f"WARNING: Failed to extract text from page {page_num+1}: {e}"
                    )

                if page_text and page_text.strip():
                    text += f"\n--- Page {page_num+1} ---\n{page_text.strip()}\n"
                else:
                    print(f"DEBUG: No text extracted from page {page_num+1}")

            # If no text and OCR is enabled
            if not text.strip() and use_ocr:
                print("INFO: No text found. Falling back to OCR...")
                images = convert_from_path(file_path)
                for i, image in enumerate(images, start=1):
                    ocr_text = pytesseract.image_to_string(image)
                    if ocr_text.strip():
                        text += f"\n--- OCR Page {i} ---\n{ocr_text.strip()}\n"

            if text.strip():
                print(f"DEBUG: Total extracted text length: {len(text)} characters")
                preview = text[:200].replace("\n", " ")
                print(f"DEBUG: Text preview: {preview}...")
            else:
                print("WARNING: No text was extracted from this PDF.")
                print("This could mean:")
                print("1. The PDF is scanned (image-based) and requires OCR")
                print("2. The PDF has unusual formatting or encoding")
                print("3. The PDF is password-protected or corrupted")

    except Exception as e:
        print(f"ERROR: Failed to extract text from PDF {file_path}: {e}")
        return ""

    return text.strip()
