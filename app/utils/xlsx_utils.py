import openpyxl
from typing import Dict, Any


def extract_data_from_xlsx(file_path: str) -> Dict[str, Any]:
    """
    Extract data from an Excel file.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        dict: Extracted data from the Excel file
    """
    try:
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        data = {}
        
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            sheet_data = []
            
            for row in sheet.iter_rows(values_only=True):
                if any(cell is not None for cell in row):
                    sheet_data.append(list(row))
            
            data[sheet_name] = sheet_data
        
        workbook.close()
        return data
    except Exception as e:
        return {"error": f"Error reading Excel file: {str(e)}"}