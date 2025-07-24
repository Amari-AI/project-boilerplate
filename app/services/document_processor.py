import os
from app.utils.pdf_utils import extract_text_from_pdf


def process_documents(file_paths):
    """
    Process different types of documents and extract relevant information.

    Args:
        file_paths: List of paths to the documents

    Returns:
        dict: Extracted data from documents
    """
    extracted_data = {}

    for file_path in file_paths:
        if file_path.endswith(".pdf"):
            extracted_data["pdf_text"] = extract_text_from_pdf(file_path)
        else:
            extracted_data["excel_text"] = ""

    extracted_data_str = ""
    for key, value in extracted_data.items():
        extracted_data_str += f"{key.upper()}:\n{value}\n\n"

    return extracted_data_str
