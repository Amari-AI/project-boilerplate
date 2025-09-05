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
        Analyze the following document data and extract key information in a structured format:
        
        {combined_text[:4000]}  # Limit to avoid token limits
        
        Please provide:
        1. Document types found
        2. Key data points extracted
        3. Summary of important information
        """

        if client_type == "openai":
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a document processing assistant that extracts and summarizes key information from business documents."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            processed_text = response.choices[0].message.content.strip()
        
        elif client_type == "anthropic":
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.3,
                system="You are a document processing assistant that extracts and summarizes key information from business documents.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            processed_text = response.content[0].text.strip()
        
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
