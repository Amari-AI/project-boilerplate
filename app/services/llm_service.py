import json
from typing import Any, Dict

import anthropic
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def extract_shipment_data(documents: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use Anthropic Claude to extract specific shipment fields from multiple documents.
    Analyzes all provided documents together to extract comprehensive information.
    
    Args:
        documents: Dictionary containing data from all processed documents
        
    Returns:
        dict: Extracted shipment fields
    """
    
    # Prepare the document content for the LLM
    document_text = ""
    messages_content = []
    
    # Process image-based PDFs first
    if documents.get("image_documents"):
        for img_doc in documents["image_documents"]:
            if img_doc.get("images") and len(img_doc["images"]) > 0:
                # Add each image document
                messages_content.append({
                    "type": "text",
                    "text": f"Document: {img_doc['filename']} (Image-based PDF)"
                })
                
                # Add first page image (usually contains the key information)
                first_page = img_doc["images"][0]
                messages_content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": first_page["image_base64"]
                    }
                })
    
    # Add all text-based PDF content
    if documents.get("pdf_documents"):
        for pdf_doc in documents["pdf_documents"]:
            document_text += f"\n--- PDF Document: {pdf_doc['filename']} ---\n"
            document_text += "=" * 50 + "\n"
            document_text += pdf_doc['text'] + "\n"
            document_text += "=" * 50 + "\n\n"
    
    # Add all Excel content
    if documents.get("excel_documents"):
        for excel_doc in documents["excel_documents"]:
            document_text += f"\n--- Spreadsheet Document: {excel_doc['filename']} ---\n"
            for sheet_name, sheet_data in excel_doc['data'].items():
                document_text += f"\nSheet: {sheet_name}\n"
                document_text += "-" * 30 + "\n"
                # Include rows to capture all data
                for row in sheet_data[:50]:  # Increased to 50 rows
                    document_text += str(row) + "\n"
                document_text += "\n"
    
    # Create document summary
    doc_summary = f"Processing {documents.get('total_files', 0)} documents:\n"
    if documents.get('pdf_documents'):
        doc_summary += f"- {len(documents['pdf_documents'])} text-based PDF(s)\n"
    if documents.get('image_documents'):
        doc_summary += f"- {len(documents['image_documents'])} image-based PDF(s)\n"
    if documents.get('excel_documents'):
        doc_summary += f"- {len(documents['excel_documents'])} Excel file(s)\n"
    
    # Create the extraction prompt
    prompt = f"""Analyze ALL the provided documents together to extract shipping/trade information.
{doc_summary}
These documents are related to the same shipment and should be analyzed collectively to find all required fields.

Extract the following information by searching across ALL documents:

1. Bill of lading number - Search all documents for "B/L NO", "Bill of Lading No", "BOL", "BL Number", or similar field
2. Container Number - Search all documents for "CNTR NO", "Container Number", "Container No", "Container ID" or similar field
3. Consignee Name - IMPORTANT: The CONSIGNEE is the receiver/recipient of the goods, NOT the shipper. Search all documents for:
   - "CONSIGNEE" section
   - "SHIP TO", "DELIVER TO", or "BUYER" field
   - Any field indicating the receiver/recipient/buyer of goods
4. Consignee Address - Extract the complete address for the consignee. Search all documents for:
   - CONSIGNEE section with address details
   - Address associated with "SHIP TO" or "DELIVER TO" company
   - If only the consignee NAME is present without an address, return null
   - DO NOT use shipper/sender address (usually under "ADDRESS", "SHIPPER", or "FROM")
5. Date - Look for shipment date, invoice date, document date, or issue date in any document
6. Line Items Count - Extract the total number of items/pieces/units. Search for:
   - "Total Pieces", "No. of Pieces", "Number of Packages", "PKG", "Pieces" field
   - If multiple documents show counts, use the most specific/detailed one
   - Count individual product rows only if no total is provided
7. Average Gross Weight - Calculate from any document containing weight information
   - Sum all weights and divide by the number of items
   - Check packing lists, bills of lading, or invoices for weight data
8. Average Price - Calculate from any document containing price information
   - Sum all "Total Value" or "Amount" values and divide by line item count
   - Usually found in invoices or commercial documents

IMPORTANT: Information may be spread across multiple documents. For example:
- Bill of Lading might have the B/L number and container number
- Invoice might have the consignee name and prices
- Packing list might have weights and item counts
Combine information from ALL documents to complete the extraction.

Documents provided:
{document_text}

Please provide the extracted information in JSON format with the following structure:
{{
    "bill_of_lading_number": "extracted value or null",
    "container_number": "extracted value or null", 
    "consignee_name": "extracted value or null",
    "consignee_address": "complete multi-line address as single string or null",
    "date": "extracted value or null",
    "line_items_count": number or null,
    "average_gross_weight": "value with unit or null",
    "average_price": "value with currency  or null"
}}

IMPORTANT EXTRACTION RULES:
1. For consignee_address: 
   - First check if there's a CONSIGNEE section with address in shipping documents
   - If not found, check near the "SHIP TO", "DELIVER TO", or "BUYER" fields in commercial documents
   - If a complete address is found, combine all lines into a single string
   - If NO consignee address is found in any document, return null
   - DO NOT use the shipper/sender/exporter address (usually under "ADDRESS", "SHIPPER", or "FROM")
2. For line_items_count: First look for a total count field. If found, use that number. Only count individual rows if no total is provided.
3. For average_gross_weight: Sum all individual weights and divide by the number of line items. Include the unit (KG, LBS, etc.).
4. For average_price: Calculate the average of the "Total Value", "Amount", or similar column - sum all total values then divide by line item count. Include currency.
5. Be precise with calculations - use actual values from the documents, not estimates.

Extract the actual values from the documents. If a field cannot be found, use null."""

    try:
        # Build the message content
        if messages_content:
            # If we have images, create a multimodal message
            messages_content.append({
                "type": "text", 
                "text": prompt
            })
            user_message = messages_content
        else:
            # Regular text-only message
            user_message = prompt
        
        response = client.messages.create(
            model='claude-sonnet-4-20250514', #"claude-opus-4-1-20250805",
            max_tokens=1000,
            temperature=0,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        # Parse the response
        response_text = response.content[0].text
        
        # Try to extract JSON from the response
        try:
            # Find JSON in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                extracted_data = json.loads(json_str)
            else:
                extracted_data = {"error": "Could not find JSON in response"}
        except json.JSONDecodeError:
            extracted_data = {"error": "Failed to parse JSON response", "raw_response": response_text}
        
        return extracted_data
        
    except Exception as e:
        return {"error": f"LLM extraction failed: {str(e)}"}