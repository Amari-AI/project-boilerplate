import os
from app.utils.pdf_utils import extract_text_from_pdf
from app.utils.excel_utils import extract_data_from_excel, format_excel_data_for_llm

def process_documents(file_paths):
    """
    Process different types of documents and extract relevant information.
    
    Args:
        file_paths: List of paths to the documents
        
    Returns:
        dict: Extracted data from documents
    """
    extracted_data = {}
    all_text = ""
    
    for file_path in file_paths:
        filename = os.path.basename(file_path)
        
        if file_path.lower().endswith(".pdf"):
            pdf_text = extract_text_from_pdf(file_path)
            extracted_data[f'pdf_{filename}'] = pdf_text
            all_text += f"\n\nDocument: {filename}\n{pdf_text}"
            
        elif file_path.lower().endswith((".xlsx", ".xls")):
            excel_data = extract_data_from_excel(file_path)
            formatted_excel = format_excel_data_for_llm(excel_data)
            extracted_data[f'excel_{filename}'] = formatted_excel
            all_text += f"\n\nDocument: {filename}\n{formatted_excel}"
    
    extracted_data['combined_text'] = all_text
    return extracted_data 