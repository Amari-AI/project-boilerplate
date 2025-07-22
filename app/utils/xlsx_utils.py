import openpyxl
import os
import base64
from typing import List, Tuple, Dict, Any

def extract_data_from_xlsx(file_path: str) -> Tuple[str, List[str]]:
    """
    Extract data from an Excel file (.xlsx).
    Returns both extracted text and base64 encoded images if available.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Tuple[str, List[str]]: Extracted text and list of base64 encoded images
    """
    text = ""
    images = []
    
    try:
        # Load the workbook
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        
        # Process each worksheet
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            
            # Add sheet header
            text += f"\n=== Sheet: {sheet_name} ===\n"
            
            # Extract cell data
            sheet_data = extract_sheet_data(sheet)
            if sheet_data:
                text += sheet_data + "\n"
            
            # Extract images from the sheet
            sheet_images = extract_images_from_sheet(sheet)
            images.extend(sheet_images)
        
        workbook.close()
        
    except Exception as e:
        print(f"Error processing Excel file: {e}")
        return f"Error reading Excel file: {str(e)}", []
    
    return text.strip() if text else "", images

def extract_sheet_data(sheet) -> str:
    """
    Extract data from a worksheet by intelligently finding the main data table.
    
    Args:
        sheet: openpyxl worksheet object
        
    Returns:
        str: Formatted text data from the sheet
    """
    data_text = ""
    
    try:
        # Get all rows with data
        rows_data = []
        for row in sheet.iter_rows():
            row_data = [str(cell.value).strip() if cell.value is not None else "" for cell in row]
            if any(row_data):
                rows_data.append(row_data)

        if not rows_data:
            return "Empty sheet\n"

        # 1. Find the header row
        header_keywords = {'s.no', 's/n', 'item', 'description', 'part no', 'qty', 'quantity', 'pcs', 'unit price', 'price', 'amount', 'total', 'hs code', 'gross weight'}
        header_row_index = -1
        best_score = 0

        for i, row in enumerate(rows_data[:20]):  # Scan first 20 rows for header
            score = sum(1 for cell in row for keyword in header_keywords if keyword in str(cell).lower())
            if score > best_score and score > 1: # Require at least 2 keywords
                best_score = score
                header_row_index = i

        if header_row_index == -1:
            # If no clear header, return a simple dump of the data
            data_text = "Could not identify a clear table header. Raw data follows:\n"
            for row in rows_data:
                data_text += " | ".join(cell for cell in row if cell) + "\n"
            return data_text

        # 2. Extract headers, line items, and summary
        headers = [h for h in rows_data[header_row_index] if h]
        data_text += f"SPREADSHEET HEADERS: {' | '.join(headers)}\n\n"

        # Data rows start after the header
        line_items = []
        summary_keywords = {'total', 'subtotal', 'grand total', 'tax', 'shipping'}
        
        for row in rows_data[header_row_index + 1:]:
            if not any(cell for cell in row): # Skip empty rows
                continue
            
            # Check if it's a summary row
            first_cell_val = str(row[0]).lower() if row and row[0] else ""
            if any(key in first_cell_val for key in summary_keywords):
                break # Stop when summary section is reached
            
            # Check for a valid line item (e.g., first column is a number or there's content)
            if (row[0] and row[0].isdigit()) or (len(row) > 1 and row[1] and len(row[1]) > 2):
                line_items.append(row)

        # 3. Format the output
        if line_items:
            data_text += f"TOTAL DATA ROWS (LINE ITEMS): {len(line_items)}\n\n"
            data_text += "LINE ITEMS:\n"
            for i, item in enumerate(line_items, 1):
                non_empty_cells = [cell for cell in item if cell]
                if i <= 25: # Show more items
                    data_text += f"Item {i}: {' | '.join(non_empty_cells)}\n"
                elif i == 26:
                    data_text += f"... and {len(line_items) - 25} more items\n"
            
            data_text += f"\nSUMMARY: This spreadsheet contains {len(line_items)} line items/products.\n"
        else:
            data_text += "No line items found after the header.\n"

    except Exception as e:
        data_text = f"Error extracting sheet data: {str(e)}\n"
    
    return data_text

def extract_images_from_sheet(sheet) -> List[str]:
    """
    Extract images from a worksheet and convert to base64.
    
    Args:
        sheet: openpyxl worksheet object
        
    Returns:
        List[str]: List of base64 encoded images
    """
    images = []
    
    try:
        # Check if sheet has images
        if hasattr(sheet, '_images') and sheet._images:
            for image in sheet._images:
                try:
                    # Get image data
                    img_data = image._data()
                    
                    # Convert to base64
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                    images.append(img_base64)
                    
                    if len(images) >= 5:  # Limit to 5 images per sheet
                        break
                        
                except Exception as e:
                    print(f"Error extracting image: {e}")
                    continue
                    
    except Exception as e:
        print(f"Error accessing sheet images: {e}")
    
    return images

def get_excel_metadata(file_path: str) -> Dict[str, Any]:
    """
    Get metadata information about the Excel file.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Dict: Metadata information
    """
    metadata = {
        'file_name': os.path.basename(file_path),
        'file_size': 0,
        'sheet_count': 0,
        'sheet_names': [],
        'error': None
    }
    
    try:
        # Get file size
        metadata['file_size'] = os.path.getsize(file_path)
        
        # Load workbook to get sheet info
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        metadata['sheet_count'] = len(workbook.sheetnames)
        metadata['sheet_names'] = workbook.sheetnames.copy()
        workbook.close()
        
    except Exception as e:
        metadata['error'] = str(e)
    
    return metadata
