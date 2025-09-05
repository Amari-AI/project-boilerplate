import csv
import os
from typing import Dict, List, Any

def extract_data_from_csv(file_path: str) -> Dict[str, Any]:
    """
    Extract data from a CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        dict: Extracted data from the CSV file
    """
    print(f"DEBUG CSV_UTILS: Attempting to read CSV: {file_path}")
    print(f"DEBUG CSV_UTILS: File exists: {os.path.exists(file_path)}")
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            # Try to detect delimiter
            sample = file.read(1024)
            file.seek(0)
            
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            print(f"DEBUG CSV_UTILS: Detected delimiter: '{delimiter}'")
            
            reader = csv.DictReader(file, delimiter=delimiter)
            rows = list(reader)
            
            print(f"DEBUG CSV_UTILS: Found {len(rows)} rows with {len(reader.fieldnames or [])} columns")
            print(f"DEBUG CSV_UTILS: Column headers: {reader.fieldnames}")
            
            return {
                'rows': rows,
                'columns': reader.fieldnames or [],
                'row_count': len(rows),
                'column_count': len(reader.fieldnames or [])
            }
            
    except Exception as e:
        print(f"ERROR CSV_UTILS: Error reading CSV {file_path}: {e}")
        return {
            'rows': [],
            'columns': [],
            'row_count': 0,
            'column_count': 0,
            'error': str(e)
        }

def format_csv_data_for_llm(csv_data: Dict[str, Any]) -> str:
    """
    Format CSV data for LLM processing.
    
    Args:
        csv_data: Dictionary containing CSV data
        
    Returns:
        str: Formatted text representation of the CSV data
    """
    if csv_data.get('error'):
        return f"Error reading CSV: {csv_data['error']}"
    
    if not csv_data.get('rows'):
        return "Empty CSV file"
    
    # Create a formatted representation
    formatted_text = f"CSV Data Summary:\n"
    formatted_text += f"- Rows: {csv_data['row_count']}\n"
    formatted_text += f"- Columns: {csv_data['column_count']}\n"
    formatted_text += f"- Headers: {', '.join(csv_data['columns'])}\n\n"
    
    # Add sample of data (first 10 rows)
    formatted_text += "Sample Data:\n"
    for i, row in enumerate(csv_data['rows'][:10]):
        formatted_text += f"Row {i+1}:\n"
        for key, value in row.items():
            if value:  # Only include non-empty values
                formatted_text += f"  {key}: {value}\n"
        formatted_text += "\n"
    
    if len(csv_data['rows']) > 10:
        formatted_text += f"... and {len(csv_data['rows']) - 10} more rows\n"
    
    return formatted_text