from anthropic import Anthropic
from app.core.config import settings
from typing import Dict, Any
import json

# Initialize the Anthropic client
# TODO: Shouldn't be hard-coded

anthropic = Anthropic(api_key=settings.ANTHROPIC_API_KEY)  # Get API key from settings

def extract_fields_from_document(document_data: Dict[str, Any], fields_to_extract: list) -> Dict[str, Any]:
    """
    Use Claude to extract specific fields from document text.
    
    Args:
        document_text: Text from the document
        fields_to_extract: List of fields to extract
        
    Returns:
        Dict: Dictionary containing extracted field values
    """
    # Serialize document data as document text
    document_text = json.dumps(document_data)
    
    # Create a specific prompt that details exactly what fields to extract
    system_prompt = "You are a document extraction assistant. Extract the requested fields accurately from the provided document and return them in valid JSON format."
    
    user_prompt = f"""
    Extract the following fields from the document text:
    {', '.join(fields_to_extract)}
    
    For each field, provide the extracted value or "Not found" if the field is not present. Extraction should be case insensitive
    Also, look for similar matches. Eg: You can use the name field if ''Consignee Name' isn't present. Similarly for 
    'Consignee Address'.

    The following fields specified in the list are special:
        - Weight - Extract the item ID : weight mapping for each item.
        - Price - Extract the item ID : price (or value) for each item.
    Format the response as a JSON object, and ONLY return the JSON without any explanation.
    
    Document text:
    {document_text[:100000]}  # Claude can handle more context
    """

    response = anthropic.messages.create(
        model="claude-3-opus-20240229",  # Or another appropriate Claude model
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,  # Lower temperature for more deterministic output
        max_tokens=1000
    )
    
    try:
        # Extract and parse the JSON response
        response_content = response.content[0].text
        print(f"Response Content: {response_content}\n\n\n")
        json_content = json.loads(response_content)
        final_content = extract_and_calculate(json_content)
        return final_content
    except json.JSONDecodeError:
        # If the response isn't valid JSON, try to extract JSON from it
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', response_content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        print(f"Error parsing response as JSON: {response_content}")
        return {"error": "Failed to parse fields from document"}
    

from datetime import date

def extract_and_calculate(data: dict) -> dict:
    output = {'Date': str(date.today())}
    line_item_count = data.get('Line Items Count')

    for key, value in data.items():
        if key in ['Weight', 'Price']:
            continue  # We'll process these separately
        else:
            output[key] = value

    if isinstance(line_item_count, int) and line_item_count > 0:
        # Calculate average weight
        if 'Weight' in data and isinstance(data['Weight'], dict):
            total_weight = sum(data['Weight'].values())
            output['Average Gross Weight'] = round(total_weight / line_item_count, 2)
        else:
            output['Average Gross Weight'] = "Not found"

        # Calculate average price
        if 'Price' in data and isinstance(data['Price'], dict):
            total_price = sum(data['Price'].values())
            output['Average Price'] = round(total_price / line_item_count, 2)
        else:
            output['Average Price'] = "Not found"
    else:
        output['Average Gross Weight'] = "Not found"
        output['Average Price'] = "Not found"

    return output
