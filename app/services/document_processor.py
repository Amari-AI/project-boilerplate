import os
import app.utils.text_utils as text_utils

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
            extracted_data['pdf_text'] = text_utils.extract_text_from_pdf(file_path)
        elif file_path.endswith(".xlsx"):
            extracted_data['xlsx_text'] = text_utils.extract_data_from_excel(file_path)
    
    
    return extracted_data