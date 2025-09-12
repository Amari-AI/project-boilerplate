import openpyxl
from typing import Dict, Any

def extract_text_from_xlsx(file_path: str) -> Dict[str, Any]:
    """
    Extract data from an XLSX file.
    
    Args:
        file_path: Path to the XLSX file
        
    Returns:
        dict: Extracted data from all sheets
    """
    data = {}
    try:
        workbook = openpyxl.load_workbook(file_path, read_only=True)
        
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            sheet_data = []
            
            for row in sheet.iter_rows(values_only=True):
                if any(cell is not None for cell in row):  # Skip empty rows
                    sheet_data.append([str(cell) if cell is not None else "" for cell in row])
            
            data[sheet_name] = sheet_data
            
        workbook.close()
    except Exception as e:
        print(f"Error extracting data from XLSX {file_path}: {str(e)}")
        return {}
    
    return data