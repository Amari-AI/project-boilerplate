import anthropic
import json
import base64
from app.core.config import settings
from app.models.shipment import ShipmentData
from app.utils.pdf_utils import get_pdf_as_base64

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

def extract_field_from_document(document_data: dict) -> ShipmentData:
    """
    Use Claude to extract specific fields from document data.
    
    Args:
        document_data: Dictionary containing document texts and data
        
    Returns:
        ShipmentData: Extracted shipment information
    """
    
    # Prepare messages for Claude
    messages = []
    text_content = ""
    
    for key, value in document_data.items():
        if key.startswith('pdf_'):
            if isinstance(value, str) and value.startswith('<SCANNED_PDF:'):
                # This is a scanned PDF, use vision processing
                file_path = value.replace('<SCANNED_PDF:', '').replace('>', '')
                pdf_base64 = get_pdf_as_base64(file_path)
                if pdf_base64:
                    text_content += f"PDF Document ({key}) - processed with vision:\n"
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"This is a PDF document ({key}). Please extract text and data from this document:"
                            },
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_base64
                                }
                            }
                        ]
                    })
                else:
                    text_content += f"PDF Document ({key}): Could not process\n\n"
            else:
                text_content += f"PDF Document ({key}):\n{value}\n\n"
        elif key.startswith('xlsx_'):
            text_content += f"Excel Document ({key}):\n{format_xlsx_data(value)}\n\n"
    
    # Main extraction prompt
    extraction_prompt = f"""
You are an expert in processing shipment documents. Extract the following information from the provided documents:

1. Bill of lading number
2. Container Number  
3. Consignee Name
4. Consignee Address
5. Date (in MM/DD/YYYY format)
6. Line Items Count (total number of different items/SKUs)
7. Average Gross Weight (calculate average weight per item if multiple items)
8. Average Price (calculate average price per item if multiple items)

Text Documents:
{text_content}

Return the extracted information as a JSON object with these exact keys:
- bill_of_lading_number
- container_number
- consignee_name
- consignee_address
- date
- line_items_count
- average_gross_weight
- average_price

If a field cannot be found, return null for that field. Be precise and accurate in your extraction.
"""

    # Add the main prompt
    if messages:
        # If we have vision content, add text extraction to the last message
        messages[-1]["content"].append({
            "type": "text", 
            "text": extraction_prompt
        })
    else:
        # No vision content, just text
        messages = [{"role": "user", "content": extraction_prompt}]

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0,
            messages=messages
        )
        
        response_text = response.content[0].text
        
        # Try to extract JSON from the response
        try:
            # Find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                extracted_data = json.loads(json_str)
            else:
                # Fallback: create empty data
                extracted_data = {}
        except json.JSONDecodeError:
            extracted_data = {}
        
        return ShipmentData(**extracted_data)
        
    except Exception as e:
        print(f"Error extracting fields with Claude: {str(e)}")
        return ShipmentData()

def format_xlsx_data(xlsx_data: dict) -> str:
    """Format XLSX data for better readability in the prompt."""
    formatted = ""
    for sheet_name, rows in xlsx_data.items():
        formatted += f"Sheet: {sheet_name}\n"
        for i, row in enumerate(rows[:20]):  # Limit to first 20 rows
            formatted += f"Row {i+1}: {' | '.join(row)}\n"
        formatted += "\n"
    return formatted
