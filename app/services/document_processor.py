import os
from app.utils.pdf_utils import extract_text_from_pdf
from app.utils.xlsx_utils import extract_text_from_xlsx

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
        filename = os.path.basename(file_path)
        
        if file_path.lower().endswith(".pdf"):
            pdf_text = extract_text_from_pdf(file_path)
            extracted_data[f'pdf_{filename}'] = pdf_text
        elif file_path.lower().endswith((".xlsx", ".xls")):
            xlsx_data = extract_text_from_xlsx(file_path)
            extracted_data[f'xlsx_{filename}'] = xlsx_data
    
    return extracted_data 