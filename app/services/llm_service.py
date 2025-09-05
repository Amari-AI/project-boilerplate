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


def extract_field_from_pdf_files(file_paths):
    """
    Use Claude's native PDF support to extract form data directly from PDF files.
    
    Args:
        file_paths: List of paths to PDF files
        
    Returns:
        dict: Extracted and processed data
    """
    print(f"DEBUG: Processing {len(file_paths)} files with Claude PDF support")
    
    # If no API key is configured, return error
    if not client or client_type != "anthropic":
        return {
            "status": "error",
            "message": "Claude PDF processing requires Anthropic API key",
            "extracted_data": {}
        }
    
    import base64
    
    # Process first PDF file (can be extended for multiple files)
    pdf_path = file_paths[0] if file_paths else None
    if not pdf_path or not pdf_path.lower().endswith('.pdf'):
        return {
            "status": "error",
            "message": "No valid PDF file provided",
            "extracted_data": {}
        }
    
    try:
        # Read PDF file as base64
        with open(pdf_path, 'rb') as f:
            pdf_data = base64.b64encode(f.read()).decode('utf-8')
        
        print(f"DEBUG: PDF file size: {len(pdf_data)} base64 characters")
        
        # Send PDF directly to Claude (using 3.5 Sonnet which supports PDFs)
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_data
                            }
                        },
                        {
                            "type": "text",
                            "text": """
                            Analyze this PDF document and extract ALL form fields and their values. This appears to be a shipping/logistics document.
                            
                            Return ONLY a JSON object with this exact structure:
                            {
                                "document_type": "type of document (e.g., Bill of Lading, Commercial Invoice, etc.)",
                                "extracted_fields": {
                                    "field_name_1": "extracted_value_1",
                                    "field_name_2": "extracted_value_2"
                                }
                            }
                            
                            CRITICAL Instructions:
                            - Extract ONLY what you can actually see in the document
                            - DO NOT invent, guess, or hallucinate any data
                            - If a field is empty or not visible, use empty string ""
                            - Use descriptive field names (e.g., "shipper_name", "consignee_address", "weight", "date")
                            - Look for common shipping document fields: shipper, consignee, notify party, description of goods, weight, dimensions, dates, reference numbers
                            - Return ONLY the JSON object, no additional text
                            """
                        }
                    ]
                }
            ]
        )
        
        processed_text = response.content[0].text.strip()
        print(f"DEBUG: Claude response: {processed_text[:500]}...")
        
        # Try to parse JSON response
        import json
        try:
            parsed_data = json.loads(processed_text)
            return {
                "status": "success",
                "message": "PDF processed successfully with Claude",
                "extracted_data": {"pdf_processed_with_claude": True},
                "structured_data": parsed_data
            }
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON parsing failed: {e}")
            print(f"DEBUG: Raw Claude response: {processed_text}")
            # Fallback: create a structured response
            return {
                "status": "success", 
                "message": "PDF processed but JSON parsing failed",
                "extracted_data": {"pdf_processed_with_claude": True},
                "structured_data": {
                    "document_type": "Unknown Document",
                    "extracted_fields": {
                        "raw_response": processed_text[:500] + ("..." if len(processed_text) > 500 else "")
                    }
                }
            }
        
    except Exception as e:
        print(f"ERROR: Claude PDF processing failed: {e}")
        return {
            "status": "error",
            "message": f"PDF processing failed: {str(e)}",
            "extracted_data": {}
        }


def extract_field_from_document_with_structured_prompt(document_data):
    """
    Use LLM to extract structured data from CSV/Excel files.
    
    Args:
        document_data: Dictionary containing extracted document data
        
    Returns:
        dict: Extracted and processed data
    """
    print(f"DEBUG: Processing structured document data with Claude")
    
    # If no API key is configured, return error
    if not client or client_type != "anthropic":
        return {
            "status": "error",
            "message": "Claude processing requires Anthropic API key",
            "extracted_data": document_data
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
        Analyze this CSV/Excel document data and extract key information in a structured format:

        {combined_text[:8000]}
        
        Return ONLY a JSON object with this exact structure:
        {{
            "document_type": "type of document (e.g., Invoice List, Customer Data, Shipment Records, etc.)",
            "extracted_fields": {{
                "key_field_1": "value_1",
                "key_field_2": "value_2"
            }}
        }}
        
        Instructions:
        - Identify the main purpose/type of this data
        - Extract the most important fields and their common values
        - If it's tabular data, summarize key patterns or totals
        - Use descriptive field names based on the column headers
        - DO NOT invent data - only extract what's clearly present
        - Return ONLY the JSON object, no additional text
        """

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        )
        
        processed_text = response.content[0].text.strip()
        print(f"DEBUG: Claude response for CSV/Excel: {processed_text[:300]}...")
        
        # Try to parse JSON response
        import json
        try:
            parsed_data = json.loads(processed_text)
            return {
                "status": "success",
                "message": "CSV/Excel processed successfully with Claude",
                "extracted_data": document_data,
                "structured_data": parsed_data
            }
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON parsing failed: {e}")
            return {
                "status": "success",
                "message": "CSV/Excel processed but JSON parsing failed", 
                "extracted_data": document_data,
                "structured_data": {
                    "document_type": "Data File",
                    "extracted_fields": {
                        "raw_response": processed_text[:500] + ("..." if len(processed_text) > 500 else "")
                    }
                }
            }
        
    except Exception as e:
        print(f"ERROR: Claude CSV/Excel processing failed: {e}")
        return {
            "status": "error",
            "message": f"CSV/Excel processing failed: {str(e)}",
            "extracted_data": document_data
        }


def process_mixed_documents(pdf_files, excel_files):
    """
    Process both PDF and Excel files together, combining their extracted data.
    
    Args:
        pdf_files: List of PDF file paths
        excel_files: List of Excel file paths
        
    Returns:
        dict: Combined extracted and processed data
    """
    print(f"DEBUG: Processing mixed documents - {len(pdf_files)} PDFs, {len(excel_files)} Excel files")
    
    if not client or client_type != "anthropic":
        return {
            "status": "error",
            "message": "Mixed document processing requires Anthropic API key",
            "extracted_data": {}
        }
    
    try:
        # Process PDF files with Claude native processing
        pdf_results = []
        for pdf_path in pdf_files:
            pdf_result = extract_field_from_pdf_files([pdf_path])
            if pdf_result.get('structured_data'):
                pdf_results.append(pdf_result['structured_data'])
        
        # Process Excel files with text-based processing
        from app.services.document_processor import process_documents
        excel_document_data = process_documents(excel_files)
        excel_result = extract_field_from_document_with_structured_prompt(excel_document_data)
        
        # Combine the results
        combined_fields = {}
        document_types = []
        
        # Add PDF fields
        for pdf_data in pdf_results:
            document_types.append(pdf_data.get('document_type', 'PDF Document'))
            combined_fields.update(pdf_data.get('extracted_fields', {}))
        
        # Add Excel fields
        if excel_result.get('structured_data'):
            excel_data = excel_result['structured_data']
            document_types.append(excel_data.get('document_type', 'Excel Document'))
            
            # Prefix Excel fields to avoid conflicts
            excel_fields = excel_data.get('extracted_fields', {})
            for key, value in excel_fields.items():
                prefixed_key = f"excel_{key}" if key not in combined_fields else f"excel_{key}"
                combined_fields[prefixed_key] = value
        
        return {
            "status": "success",
            "message": f"Mixed documents processed successfully - {len(pdf_files)} PDF(s), {len(excel_files)} Excel file(s)",
            "extracted_data": {"mixed_processing": True},
            "structured_data": {
                "document_type": " + ".join(document_types) if document_types else "Mixed Documents",
                "extracted_fields": combined_fields
            }
        }
        
    except Exception as e:
        print(f"ERROR: Mixed document processing failed: {e}")
        return {
            "status": "error",
            "message": f"Mixed document processing failed: {str(e)}",
            "extracted_data": {}
        }


def extract_field_from_document(document_data):
    """
    Legacy function for backward compatibility - now just returns error for text-based processing
    """
    return {
        "status": "error",
        "message": "Text-based processing deprecated - use structured processing instead", 
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
