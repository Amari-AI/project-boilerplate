import anthropic
import json
from app.core.config import settings
from app.models.shipment import ShipmentData

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

def extract_field_from_document(document_data: dict) -> ShipmentData:
    """
    Use Claude to extract specific fields from document data.
    
    Args:
        document_data: Dictionary containing document texts and data
        
    Returns:
        ShipmentData: Extracted shipment information
    """
    
    # Prepare document content for Claude
    document_content = ""
    for key, value in document_data.items():
        if key.startswith('pdf_'):
            document_content += f"PDF Document ({key}):\n{value}\n\n"
        elif key.startswith('xlsx_'):
            document_content += f"Excel Document ({key}):\n{format_xlsx_data(value)}\n\n"
    
    prompt = f"""
        You are an expert in processing shipment documents. Extract the following information from the provided documents:

        1. Bill of lading number
        2. Container Number  
        3. Consignee Name
        4. Consignee Address
        5. Date (in MM/DD/YYYY format)
        6. Line Items Count
        7. Average Gross Weight
        8. Average Price

        Documents:
        {document_content}

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

    try:
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0,
            messages=[
                {"role": "user", "content": prompt}
            ]
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
