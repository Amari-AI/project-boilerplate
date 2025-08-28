import os
from app.utils.pdf_utils import extract_text_from_pdf, extract_pdf_as_image_data
from app.utils.xlsx_utils import extract_data_from_xlsx
from typing import Dict, Any, List


def process_documents(file_paths: List[str]) -> Dict[str, Any]:
    """
    Process different types of documents and extract relevant information.
    Handles any number of PDFs and Excel files.
    
    Args:
        file_paths: List of paths to the documents
        
    Returns:
        dict: Extracted data from all documents
    """
    extracted_data = {
        'pdf_documents': [],
        'excel_documents': [],
        'all_text_content': '',
        'all_excel_data': {},
        'image_documents': []
    }
    
    pdf_count = 0
    excel_count = 0
    
    for file_path in file_paths:
        file_ext = os.path.splitext(file_path)[1].lower()
        filename = os.path.basename(file_path)
        
        if file_ext == ".pdf":
            pdf_count += 1
            # Extract text from PDF
            pdf_text = extract_text_from_pdf(file_path)
            
            # Check if it's an image-based PDF
            if "[IMAGE_PDF:" in pdf_text:
                pdf_images = extract_pdf_as_image_data(file_path)
                extracted_data['image_documents'].append({
                    'filename': filename,
                    'images': pdf_images.get('images', []),
                    'type': 'pdf_image'
                })
            else:
                # Add text content
                extracted_data['pdf_documents'].append({
                    'filename': filename,
                    'text': pdf_text
                })
                extracted_data['all_text_content'] += f"\n\n--- PDF Document: {filename} ---\n{pdf_text}\n"
            
        elif file_ext in [".xlsx", ".xls"]:
            excel_count += 1
            # Extract data from Excel file
            xlsx_data = extract_data_from_xlsx(file_path)
            
            extracted_data['excel_documents'].append({
                'filename': filename,
                'data': xlsx_data
            })
            
            # Merge all Excel data with unique sheet names
            for sheet_name, sheet_data in xlsx_data.items():
                unique_sheet_name = f"{filename}_{sheet_name}"
                extracted_data['all_excel_data'][unique_sheet_name] = sheet_data
    
    # Add metadata
    extracted_data['total_files'] = len(file_paths)
    extracted_data['pdf_count'] = pdf_count
    extracted_data['excel_count'] = excel_count
    extracted_data['file_types'] = [os.path.splitext(fp)[1].lower() for fp in file_paths]
    
    return extracted_data