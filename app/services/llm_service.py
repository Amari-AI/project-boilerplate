# from openai import OpenAI
import base64
from anthropic import Anthropic
from anthropic.types import ToolUseBlock

from app.core.config import settings
from app.services.excel_processor import excel_to_csv_strings_all_sheets
from app.core.models import (
    BillOfLading,
    Invoice,
    InvoiceItem,
    BillOfLading,
    ExtractedData,
)

client = Anthropic(api_key=settings.API_KEY)


def extract_invoice_list(excel_file_path: str) -> Invoice | None:
    """
    Use LLM to extract invoice list from excel data.

    Args:
        excel_data: Excel data

    Returns:
        list[str]: Invoice list
    """

    system_prompt = """
    You are a helpful assistant that extracts invoice data for user from unstructured excel data.

    No need to write any other text than the invoice list.
    """

    excel_data = excel_to_csv_strings_all_sheets(excel_file_path)
    excel_data_str = ""
    for key, value in excel_data.items():
        excel_data_str += f"Sheet: {key}\nData:\n{value}\n\n"

    response = client.messages.create(
        system=system_prompt,
        messages=[{"role": "user", "content": excel_data_str}],
        model="claude-3-5-haiku-latest",
        max_tokens=1000,
        tools=[
            {
                "name": "extract_invoice_list",
                "description": "Extract invoice list from excel data",
                "input_schema": Invoice.model_json_schema(),
            }
        ],
        temperature=0,
    )

    # print(f"extract_invoice_list: {response=}")
    for message in response.content:
        if isinstance(message, ToolUseBlock):
            return message.input
    return None


def extract_bill_of_lading_list(pdf_path: str) -> BillOfLading | None:
    with open(pdf_path, "rb") as file:
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": base64.b64encode(file.read()).decode("utf-8"),
                        },
                    }
                ],
            }
        ]

    response = client.messages.create(
        system="Extract Bill of Lading data from the given documents. Summarize the data in a structured format.",
        messages=messages,
        model="claude-3-5-haiku-latest",
        max_tokens=300,
        tools=[
            {
                "name": "extract_bill_of_lading",
                "description": "Extract bill of lading data from the given document",
                "input_schema": BillOfLading.model_json_schema(),
            }
        ],
        temperature=0,
    )

    # print(f"extract_bill_of_lading_list: {response=}")
    for message in response.content:
        if isinstance(message, ToolUseBlock):
            return message.input
    return None


def extract_field_from_document(file_paths: list[str]) -> ExtractedData:
    """
    Use LLM to extract specific field from document text.

    Args:
        document_text: Text from the document

    Returns:
        str: Extracted field value
    """

    bill_of_lading_data = None
    invoice_data = None

    for file_path in file_paths:
        if file_path.lower().endswith(".pdf"):
            bill_of_lading_data = (
                extract_bill_of_lading_list(file_path) or bill_of_lading_data
            )
            print(f"bill_of_lading_data: {bill_of_lading_data=}")
        elif file_path.lower().endswith(".xlsx"):
            invoice_data = extract_invoice_list(file_path) or invoice_data
            print(f"invoice_data: {invoice_data=}")

    print(f"bill_of_lading_data: {bill_of_lading_data=}")
    print(f"invoice_data: {invoice_data=}")

    return ExtractedData(
        bill_of_lading_list=bill_of_lading_data, invoice_list=invoice_data
    )
