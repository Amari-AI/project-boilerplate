import anthropic
import json
from app.core.config import settings
from typing import List, Optional, Dict, Any

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def extract_field_from_document(document_text: str, images: List[str] = None) -> Dict[str, Any]:
    """
    Use LLM to extract specific fields from ALL document content (text and images combined).
    Processes all available data together to find complementary information across documents.
    
    Args:
        document_text: Combined text from all documents
        images: List of base64 encoded images from all documents (optional)
        
    Returns:
        Dict[str, Any]: Dictionary with extracted field values
    """
    
    # Check if we have any content to process
    has_text = document_text and document_text.strip()
    has_images = images and len(images) > 0
    
    if has_text and has_images:
        # Use combined text and vision model extraction for maximum data coverage
        return extract_from_combined_sources(document_text, images)
    elif has_text:
        # Use text-based extraction only
        return extract_from_text(document_text)
    elif has_images:
        # Use vision model extraction only
        return extract_from_images(images)
    else:
        return {
            "bill_of_lading_number": None,
            "container_number": None,
            "consignee_name": None,
            "consignee_address": None,
            "date": None,
            "line_items_count": None,
            "average_gross_weight": None,
            "average_price": None,
            "error": "No extractable content found in document"
        }


def extract_from_combined_sources(document_text: str, images: List[str]) -> Dict[str, Any]:
    """
    Extract data using both text and images to get the most complete information.
    This handles cases where information is split across different document types.
    """
    
    # Prepare content with both text and images
    content = [
        {
            "type": "text",
            "text": f"""Extract the following information from ALL the provided content (both text and images). The documents may contain complementary information - use ALL sources to provide the most complete and accurate data.

Text content from documents:
{document_text}

Required fields to extract (use information from ALL sources):
- bill_of_lading_number: The bill of lading number (string or null if not found)
- container_number: The container number (string or null if not found)  
- consignee_name: The name of the consignee/recipient (string or null if not found)
- consignee_address: The full address of the consignee (string or null if not found)
- date: The document date in YYYY-MM-DD format (string or null if not found)
- line_items_count: The total number of line items/products/rows in the invoice/manifest. Look for "TOTAL DATA ROWS", "LINE ITEMS:", item counts, or count the actual data rows in spreadsheets. This should be the total count of all products/items, not just 1. (integer or null if not found)
- average_gross_weight: The average gross weight per item (number or null if not found)
- average_price: The average price per item (number or null if not found)

IMPORTANT: Look for information in BOTH the text above AND the images below. Some fields might only be visible in images, others only in text. Combine all available information to provide the most complete response.

For line_items_count specifically:
- Look for explicit counts like "TOTAL DATA ROWS: X" or "SUMMARY: This spreadsheet contains X line items"
- Count actual item rows in spreadsheet data (e.g., if you see "Item 1:", "Item 2:", etc., count them)
- Look for invoice line items, product lists, or manifest entries
- If you see numbered items or rows of products, count the total number

Return only valid JSON with the exact field names above. If a field cannot be found in ANY source, set it to null. Do not include any explanation text."""
        }
    ]
    
    # Add up to 5 images when combining sources (more allowance since we're doing comprehensive extraction)
    for i, image_base64 in enumerate(images[:5]):
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": image_base64
            }
        })
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,  # Increased for more complex processing
            temperature=0.1,
            messages=[
                {"role": "user", "content": content}
            ]
        )
        
        response_text = response.content[0].text.strip()
        
        # Try to parse as JSON
        try:
            extracted_data = json.loads(response_text)
            return validate_and_clean_data(extracted_data)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from the response
            return extract_json_from_response(response_text)
            
    except Exception as e:
        return create_error_response(f"Error processing combined sources: {str(e)}")


def extract_from_text(document_text: str) -> Dict[str, Any]:
    """Extract structured data from text using Claude."""
    
    prompt = f"""Extract the following information from ALL the document text provided. The text may come from multiple documents (PDFs, Excel files, etc.) - use ALL available information to provide the most complete response.

Document text from all sources:
{document_text}

Required fields:
- bill_of_lading_number: The bill of lading number (string or null if not found)
- container_number: The container number (string or null if not found)  
- consignee_name: The name of the consignee/recipient (string or null if not found)
- consignee_address: The full address of the consignee (string or null if not found)
- date: The document date in YYYY-MM-DD format (string or null if not found)
- line_items_count: The total number of line items/products/rows in the invoice/manifest. Look for "TOTAL DATA ROWS", "LINE ITEMS:", item counts, or count the actual data rows in spreadsheets. This should be the total count of all products/items, not just 1. (integer or null if not found)
- average_gross_weight: The average gross weight per item (number or null if not found)
- average_price: The average price per item (number or null if not found)

For line_items_count specifically:
- Look for explicit counts like "TOTAL DATA ROWS: X" or "SUMMARY: This spreadsheet contains X line items"
- Count actual item rows in spreadsheet data (e.g., if you see "Item 1:", "Item 2:", etc., count them)
- Look for invoice line items, product lists, or manifest entries
- If you see numbered items or rows of products, count the total number

Return only valid JSON with the exact field names above. If a field cannot be found, set it to null. Do not include any explanation text."""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = response.content[0].text.strip()
        
        # Try to parse as JSON
        try:
            extracted_data = json.loads(response_text)
            return validate_and_clean_data(extracted_data)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from the response
            return extract_json_from_response(response_text)
            
    except Exception as e:
        return create_error_response(f"Error processing text: {str(e)}")


def extract_from_images(images: List[str]) -> Dict[str, Any]:
    """Extract structured data from images using Claude's vision capabilities."""
    
    # Prepare content with images
    content = [
        {
            "type": "text",
            "text": """Extract the following information from ALL the document images provided. The images may be from different documents (PDFs, scanned files, etc.) that contain related information. Look across ALL images to provide the most complete response.

Required fields (search ALL images):
- bill_of_lading_number: The bill of lading number (string or null if not found)
- container_number: The container number (string or null if not found)  
- consignee_name: The name of the consignee/recipient (string or null if not found)
- consignee_address: The full address of the consignee (string or null if not found)
- date: The document date in YYYY-MM-DD format (string or null if not found)
- line_items_count: The total number of line items/products/rows visible in the images. Count all visible product entries, invoice lines, or manifest items across all images. This should be the total count, not just 1. (integer or null if not found)
- average_gross_weight: The average gross weight per item (number or null if not found)
- average_price: The average price per item (number or null if not found)

IMPORTANT: Examine ALL images carefully. Information might be split across different pages or documents. Use information from ALL sources to provide the most complete and accurate data.

For line_items_count specifically:
- Count all visible line items, product entries, or rows in tables across all images
- Look for numbered items (1, 2, 3, etc.) or product listings
- If you see multiple pages of items, count items from all pages
- Don't just return 1 unless there's truly only one item visible

Return only valid JSON with the exact field names above. If a field cannot be found in ANY image, set it to null. Do not include any explanation text."""
        }
    ]
    
    # Add up to 5 images to get comprehensive coverage
    for i, image_base64 in enumerate(images[:5]):
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": image_base64
            }
        })
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0.1,
            messages=[
                {"role": "user", "content": content}
            ]
        )
        
        response_text = response.content[0].text.strip()
        
        # Try to parse as JSON
        try:
            extracted_data = json.loads(response_text)
            return validate_and_clean_data(extracted_data)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from the response
            return extract_json_from_response(response_text)
            
    except Exception as e:
        return create_error_response(f"Error processing images with vision model: {str(e)}")


def validate_and_clean_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean the extracted data."""
    
    # Define the expected structure
    expected_fields = {
        "bill_of_lading_number": str,
        "container_number": str,
        "consignee_name": str,
        "consignee_address": str,
        "date": str,
        "line_items_count": int,
        "average_gross_weight": (int, float),
        "average_price": (int, float)
    }
    
    cleaned_data = {}
    
    for field, expected_type in expected_fields.items():
        value = data.get(field)
        
        if value is None or value == "" or value == "null":
            cleaned_data[field] = None
        else:
            try:
                if expected_type == str:
                    cleaned_data[field] = str(value).strip()
                elif expected_type == int:
                    cleaned_data[field] = int(float(value)) if value else None
                elif expected_type == (int, float):
                    cleaned_data[field] = float(value) if value else None
            except (ValueError, TypeError):
                cleaned_data[field] = None
    
    return cleaned_data


def extract_json_from_response(response_text: str) -> Dict[str, Any]:
    """Try to extract JSON from a response that might contain extra text."""
    
    # Look for JSON-like content between braces
    import re
    
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, response_text, re.DOTALL)
    
    for match in matches:
        try:
            data = json.loads(match)
            return validate_and_clean_data(data)
        except json.JSONDecodeError:
            continue
    
    # If no valid JSON found, return error
    return create_error_response("Could not parse structured data from response")


def create_error_response(error_message: str) -> Dict[str, Any]:
    """Create a standardized error response."""
    return {
        "bill_of_lading_number": None,
        "container_number": None,
        "consignee_name": None,
        "consignee_address": None,
        "date": None,
        "line_items_count": None,
        "average_gross_weight": None,
        "average_price": None,
        "error": error_message
    }
