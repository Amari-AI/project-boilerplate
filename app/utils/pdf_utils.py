import PyPDF2
import os
from typing import Optional, List


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        str: Extracted text from the PDF file
    """

    print(f"extract_text_from_pdf: {file_path=}")

    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            print(f"extract_text_from_pdf: {page=}")
            text += page.extract_text()

    print(f"extract_text_from_pdf: {text=}")
    return text
