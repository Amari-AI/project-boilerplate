import os
from app.utils.pdf_utils import extract_text_from_pdf
from app.utils.xlsx_utils import extract_data_from_xlsx, get_excel_metadata
from typing import Dict, Any, List

def process_documents(file_paths: List[str]) -> Dict[str, Any]:
    """
    Process different types of documents and extract relevant information.
    
    Args:
        file_paths: List of paths to the documents
        
    Returns:
        dict: Extracted data from documents including text and images
    """
    extracted_data = {
        'text': '',
        'images': [],
        'file_info': []
    }
    
    for file_path in file_paths:
        file_info = {
            'path': file_path,
            'name': os.path.basename(file_path),
            'type': 'unknown'
        }
        
        if file_path.endswith(".pdf"):
            file_info['type'] = 'pdf'
            pdf_text, pdf_images = extract_text_from_pdf(file_path)
            
            if pdf_text:
                extracted_data['text'] += f"\n--- {file_info['name']} ---\n{pdf_text}\n"
                file_info['has_text'] = True
            else:
                file_info['has_text'] = False
                
            if pdf_images:
                extracted_data['images'].extend(pdf_images)
                file_info['image_count'] = len(pdf_images)
            else:
                file_info['image_count'] = 0
        
        elif file_path.endswith((".xlsx", ".xls")):
            file_info['type'] = 'excel'
            
            # Get Excel metadata
            metadata = get_excel_metadata(file_path)
            file_info['sheet_count'] = metadata.get('sheet_count', 0)
            file_info['sheet_names'] = metadata.get('sheet_names', [])
            file_info['file_size'] = metadata.get('file_size', 0)
            
            if metadata.get('error'):
                file_info['error'] = metadata['error']
                file_info['has_text'] = False
                file_info['image_count'] = 0
            else:
                # Extract data from Excel
                excel_text, excel_images = extract_data_from_xlsx(file_path)
                
                if excel_text:
                    extracted_data['text'] += f"\n--- {file_info['name']} ---\n{excel_text}\n"
                    file_info['has_text'] = True
                else:
                    file_info['has_text'] = False
                    
                if excel_images:
                    extracted_data['images'].extend(excel_images)
                    file_info['image_count'] = len(excel_images)
                else:
                    file_info['image_count'] = 0
                
        extracted_data['file_info'].append(file_info)
    
    return extracted_data 