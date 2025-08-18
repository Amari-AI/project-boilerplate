BILL_OF_LADING_NUMBER_PROMPT = """
You are tasked with extracting the bill of lading number from a set of documents.

The documents are provided below:

<documents>
<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>

<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>
</documents>

Your goal is to carefully examine all documents as a complete set and locate the bill of lading number. The bill of lading number is a unique identifier for a specific shipment, typically consisting of a combination of letters and numbers.

Follow these steps:

1. Scan through all documents, looking for any mention of "bill of lading," "B/L," or "BOL" followed by a number.

2. The bill of lading number typically appears in formats such as "ABCD1234567" or "123-456789".

3. Pay attention to headers, tables, or sections that might contain shipping information, as the bill of lading number is often found in these areas.

4. If you find multiple potential bill of lading numbers across the documents, choose the one that appears to be the primary or most relevant to the shipment described in the document set.

5. If you cannot find a clear bill of lading number, look for similar identifiers such as "Shipping Number," "Consignment Number," or "Tracking Number" that might serve a similar purpose.

Present your findings in the following format:

<result>
[Insert either the bill of lading number you found or "Not found"]
</result>

<explanation>
[Provide a brief explanation of where you found the number in the documents, or why you were unable to locate it]
</explanation>

Remember to focus solely on extracting the bill of lading number from the provided document set. Do not make assumptions or add information that is not present in the given text.
""".strip()

CONTAINER_NUMBER_PROMPT = """
You are tasked with extracting the container number from a set of documents.

The documents are provided below:

<documents>
<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>

<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>
</documents>

Your goal is to identify and extract the container number from this document set. A container number is a unique identifier that typically follows this format:
- 4 letters (usually representing the owner code)
- 7 numbers  
- 1 check digit (example: ABCD1234567-8)

Follow these steps:

1. Carefully read through all documents in the set.

2. Look for any sequence of characters that matches the container number format described above.

3. If you find multiple matching sequences across the documents, choose the one that appears to be the most likely container number based on context (e.g., if it's near words like "container", "shipment", or "cargo").

4. Consider the context and relevance of each potential match to determine the primary container number for this shipment.

Present your findings in the following format:

<result>
[Insert the extracted container number or "Not found"]
</result>

<explanation>
[Provide a brief explanation of where you found the number in the documents, or why you were unable to locate it. If there were multiple potential matches, explain your reasoning for the selection.]
</explanation>

Remember to focus solely on extracting the container number. Do not provide any additional information or analysis about the documents unless it directly relates to identifying the container number.
""".strip()

CONSIGNEE_NAME_PROMPT = """
You are tasked with extracting the consignee name from a set of documents.

The documents are provided below:

<documents>
<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>

<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>
</documents>

Your goal is to identify and extract the consignee name from this document set. The consignee name refers to the person or entity receiving the goods or services described in the documents.

Follow these steps:

1. Look for labels such as "Consignee:", "Ship To:", or "Recipient:" across all documents.

2. The consignee name is often located near the top of documents, in header or address sections.

3. It may be a person's name, a company name, or a combination of both.

4. Be aware that documents may use different terminology, such as "Buyer" or "Customer".

5. If multiple documents contain consignee information, ensure consistency and select the most complete or authoritative reference.

Present your findings in the following format:

<result>
[Insert the consignee name you found or "Not found"]
</result>

<explanation>
[Provide a brief explanation of where you found the consignee name in the documents, or why you were unable to locate it. If multiple references existed, explain how you determined the final answer.]
</explanation>

Remember to focus solely on extracting the consignee name. Do not include any other information from the documents in your response.
""".strip()

CONSIGNEE_PROMPT = """
You are tasked with extracting the consignee from a set of documents.

The documents are provided below:

<documents>
<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>

<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>
</documents>

Your goal is to identify and extract the consignee from this document set. The consignee is typically the party to whom goods or a shipment is to be delivered.

Follow these steps:

1. Look for terms like "Consignee:", "Ship To:", or "Deliver To:" which often precede the consignee's information across all documents.

2. The consignee is usually a company name, but it could also be an individual's name.

3. Extract only the name of the consignee, not the full address or contact details.

4. The consignee information is typically found near the top of shipping documents, invoices, or bills of lading.

5. If you find multiple potential consignees across the documents, choose the one that seems most authoritative or consistent based on the context of the document set.

Present your findings in the following format:

<result>
[Insert the consignee name you found or "Not found"]
</result>

<explanation>
[Provide a brief explanation of where you found the consignee in the documents, or why you were unable to locate it. If there were multiple potential consignees, explain your reasoning for the selection.]
</explanation>

Remember to focus solely on extracting the consignee name. Do not include any other information from the documents unless it directly relates to identifying the consignee.
""".strip()

DATE_PROMPT = """
You are tasked with extracting the date from a set of documents.

The documents are provided below:

<documents>
<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>

<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>
</documents>

Your goal is to accurately identify and extract the most relevant date from this document set. The documents may include bills of lading (PDF format) and commercial invoices/packing lists (Excel format).

Follow these steps:

1. Examine all documents to determine their types based on content and structure.

2. Look for dates in the following locations across all documents:
   - For bills of lading (PDF): Look for fields labeled "Date", "Issue Date", or "Date of Issue" in headers, top corners, or structured sections.
   - For commercial invoices and packing lists (Excel): Look for columns or cells labeled "Date", "Invoice Date", or "Shipment Date" in top rows or header sections.

3. When you find dates, verify that they follow logical formats (e.g., DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD). Be aware that date formats may vary between documents.

4. If you encounter multiple dates across the document set, prioritize the most relevant one based on context (e.g., issue date, shipment date).

5. Convert the selected date to YYYY-MM-DD format for consistency.

Present your findings in the following format:

<result>
[Insert the extracted date in YYYY-MM-DD format or "Not found"]
</result>

<explanation>
[Provide a brief explanation of where you found the date in the documents, what type of date it was (e.g., issue date, shipment date), and any challenges you encountered. If multiple dates were present across documents, explain your selection reasoning.]
</explanation>

Remember to focus solely on extracting the most relevant date from the provided document set. Do not make assumptions about dates that are not clearly present in the given text.
""".strip()

LINE_ITEMS_COUNT_PROMPT = """
You are tasked with extracting the line items count from a set of documents.

The documents are provided below:

<documents>
<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>

<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>
</documents>

Your goal is to identify and extract the line items count from this document set. This field represents the number of line items in an invoice or similar document and may be represented as "Number of Items:", "Line Items:", or "Total Items:".

Follow these steps:

1. Scan all documents for any mention of line items or a count of items.

2. If you find relevant fields across multiple documents, extract the numerical value that appears most authoritative or consistent.

3. If there are multiple potential matches across the document set, choose the one that most accurately represents the total number of line items for this shipment.

4. Do not attempt to calculate the count from other information - only extract explicitly stated values.

5. Consider the context and document type to determine which count is most relevant to the overall shipment.

Present your findings in the following format:

<result>
[Insert the line items count number or "Not found"]
</result>

<explanation>
[Provide a brief explanation of where you found the count in the documents, or why you were unable to locate it. If multiple counts existed across documents, explain your selection reasoning.]
</explanation>

Remember:
- Only extract explicitly stated line item counts
- Do not calculate or infer the count from other information
- Focus solely on extracting the most relevant line items count for this document set
""".strip()

AVERAGE_GROSS_WEIGHT_PROMPT = """
You are tasked with extracting the average gross weight from a set of documents.

The documents are provided below:

<documents>
<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>

<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>
</documents>

Your goal is to locate and extract the average gross weight from this document set. This field represents an important shipping metric and may be presented in various formats such as "Average Gross Weight:", "Avg. Gross Weight:", or "average_gross_weight".

Follow these steps:

1. Scan all documents for variations of the "average gross weight" field.

2. Once located, extract the associated value, which should typically be a numerical figure.

3. If the value is presented with a unit of measurement (e.g., kg, lbs, tons), include the unit in your extraction.

4. If multiple documents contain average gross weight information, select the most authoritative or consistent value based on document type and context.

5. If multiple potential values exist across the document set, choose the one that most clearly represents the average gross weight for this shipment.

Present your findings in the following format:

<result>
[Insert the average gross weight value with units or "Not found"]
</result>

<explanation>
[Provide a brief explanation of where you found the average gross weight in the documents, or why you were unable to locate it. If multiple values existed across documents, explain your selection reasoning.]
</explanation>

Remember to focus solely on extracting the average gross weight field. Do not extract or report on any other information from the documents unless it directly relates to this specific field.
""".strip()

AVERAGE_PRICE_PROMPT = """
You are tasked with extracting the average price from a set of documents.

The documents are provided below:

<documents>
<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>

<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>
</documents>

Your goal is to identify and extract the average price from this document set. This field represents the average price of an item or service mentioned in the documents.

Follow these steps:

1. Scan all documents for any mention of "average price," "avg price," "mean price," or similar variations.

2. Look for numerical values associated with these phrases across all documents.

3. Pay attention to currency symbols or abbreviations (e.g., $, USD, EUR) that may precede or follow the numerical value.

4. If multiple documents contain average price information, select the most authoritative or consistent value based on document context.

5. If the average price appears ambiguous or unclear, provide your best estimate based on the available information.

Present your findings in the following format:

<result>
[Insert the average price with currency or "Not found"]
</result>

<explanation>
[Provide a brief explanation of where you found the average price in the documents, or why you were unable to locate it. If multiple prices existed across documents, explain your selection reasoning. If the price was ambiguous, note any uncertainty.]
</explanation>

Remember to focus solely on extracting the average price field. Do not include any additional analysis or information from the documents unless it directly relates to identifying the average price.
""".strip()

DEFAULT_PROMPT = """
You are tasked with extracting the {field_name} from a set of documents.

The documents are provided below:

<documents>
<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>

<document>
{{DOCUMENT_NAME}}
{{DOCUMENT_CONTENT}}
</document>
</documents>

Your goal is to carefully examine this document set and locate the {field_name}. The {field_name} may be presented in various formats depending on the document type.

Follow these steps:

1. Scan through all documents, looking for any mention of "{field_name}" or related terminology that might indicate this field.

2. Look for labels, headers, or sections that might contain this information across all documents.

3. Pay attention to tables, forms, or structured sections where such data is typically found.

4. If you find multiple potential values for {field_name} across the documents, choose the one that appears to be the most relevant and accurate based on the document context.

5. If you cannot find a clear {field_name} value, look for similar or related fields that might serve the same purpose.

Present your findings in the following format:

<result>
[Insert either the {field_name} value you found or "Not found"]
</result>

<explanation>
[Provide a brief explanation of where you found the value in the documents, or why you were unable to locate it. If multiple potential values existed across documents, explain your selection reasoning.]
</explanation>

Remember to focus solely on extracting the {field_name} from the provided document set. Do not include any other information from the documents unless it directly relates to identifying this specific field.
""".strip()

PROMPTS = {
    "bill_of_lading_number": BILL_OF_LADING_NUMBER_PROMPT,
    "container_number": CONTAINER_NUMBER_PROMPT,
    "consignee_name": CONSIGNEE_NAME_PROMPT,
    "consignee": CONSIGNEE_PROMPT,
    "date": DATE_PROMPT,
    "line_items_count": LINE_ITEMS_COUNT_PROMPT,
    "average_gross_weight": AVERAGE_GROSS_WEIGHT_PROMPT,
    "average_price": AVERAGE_PRICE_PROMPT,
}


def get_prompt(field_name: str, documents: dict = None) -> str:
    """
    Get a formatted prompt for extracting a specific field from documents.

    Args:
        field_name (str): The name of the field to extract
        documents (dict): Dictionary where keys are document names and values are document content
                         Example: {"invoice.pdf": "content...", "bill_of_lading.pdf": "content..."}

    Returns:
        str: Formatted prompt with documents interpolated
    """
    if documents is None:
        documents = {}

    prompt = PROMPTS.get(field_name, DEFAULT_PROMPT)

    # Format the documents into the expected structure
    formatted_documents = ""
    for doc_name, doc_content in documents.items():
        formatted_documents += f"<document>\n{doc_name}\n{doc_content}\n</document>\n\n"

    # Remove the trailing newlines
    formatted_documents = formatted_documents.rstrip()

    # Replace the entire documents section with the formatted documents
    # Find the documents section and replace it
    documents_start = prompt.find("<documents>")
    documents_end = prompt.find("</documents>") + len("</documents>")

    if documents_start != -1 and documents_end != -1:
        before_documents = prompt[:documents_start]
        after_documents = prompt[documents_end:]
        formatted_prompt = (
            before_documents
            + f"<documents>\n{formatted_documents}\n</documents>"
            + after_documents
        )
    else:
        # Fallback to original logic if document tags are not found
        formatted_prompt = prompt

    # Format any field_name placeholders
    formatted_prompt = formatted_prompt.format(field_name=field_name)

    return formatted_prompt
