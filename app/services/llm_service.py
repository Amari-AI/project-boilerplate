from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from anthropic import Anthropic
from app.core.config import settings

# Initialize client based on available API key
if settings.OPENAI_API_KEY:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    client_type = "openai"
elif settings.ANTHROPIC_API_KEY:
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    client_type = "anthropic"
else:
    client = None
    client_type = None


def extract_field_from_document(document_data):
    """
    Use LLM to extract specific field from document text.
    
    Args:
        document_data: Dictionary containing extracted document data
        
    Returns:
        dict: Extracted and processed data
    """
    
    # If no API key is configured, return the raw extracted data
    if not client:
        return {
            "status": "success",
            "message": "Document processed successfully (LLM processing disabled - no API key)",
            "extracted_data": document_data,
            "processed_data": "LLM processing requires API key configuration"
        }
    
    # Use the combined text for LLM processing
    combined_text = document_data.get('combined_text', '')
    
    if not combined_text.strip():
        return {
            "status": "error",
            "message": "No text could be extracted from the uploaded documents",
            "extracted_data": document_data
        }
    
    try:
        prompt = f"""
        You are a form data extraction expert. Analyze the following document and extract ALL form fields, labels, and their values. 
        Look for boxes, fields, labels, and any structured data entry areas.
        
        Document content:
        {combined_text[:4000]}
        
        Return the extracted data as a JSON object with this exact structure:
        {{
            "document_type": "type of document (e.g., Bill of Lading, Commercial Invoice, etc.)",
            "extracted_fields": {{
                "field_name_1": "extracted_value_1",
                "field_name_2": "extracted_value_2",
                "field_name_3": "extracted_value_3"
            }}
        }}
        
        Instructions:
        - Extract ALL visible form fields, even if empty
        - Use descriptive field names (e.g., "shipper_name", "consignee_address", "weight", "date")
        - If a field is empty, use empty string ""
        - Look for common shipping document fields: shipper, consignee, notify party, description of goods, weight, dimensions, dates, reference numbers
        - Return ONLY the JSON object, no additional text
        """

        if client_type == "openai":
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a document processing assistant that extracts and summarizes key information from business documents."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            processed_text = response.choices[0].message.content.strip()
        
        elif client_type == "anthropic":
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=800,
                temperature=0.3,
                system="You are a document processing assistant that extracts and summarizes key information from business documents.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            processed_text = response.content[0].text.strip()
        
        # Try to parse as JSON, fallback to plain text if it fails
        import json
        try:
            parsed_data = json.loads(processed_text.strip())
            return {
                "status": "success",
                "message": "Documents processed successfully",
                "extracted_data": document_data,
                "structured_data": parsed_data
            }
        except json.JSONDecodeError:
            # Fallback to plain text if JSON parsing fails
            processed_text = processed_text.replace('\\n', '\n')
            if len(processed_text) > 800:
                processed_text = processed_text[:800] + "..."
        
        return {
            "status": "success",
            "message": "Documents processed successfully",
            "extracted_data": document_data,
            "processed_data": processed_text
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"LLM processing failed: {str(e)}",
            "extracted_data": document_data
        }
