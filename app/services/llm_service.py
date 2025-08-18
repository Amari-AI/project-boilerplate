import json
import asyncio
from typing import Any, List, Union
from datetime import datetime
import anthropic
from app.core.config import settings
from app.core.models import ExtractedData
from .prompts import get_prompt

client = anthropic.AsyncAnthropic(api_key=settings.API_KEY)


async def extract_field_from_documents(
    field_name: str, data_type: str = None, documents: List[str] = None
) -> Any:
    """
    Use Claude to extract specific field from document texts using structured outputs.

    Args:
        field_name: Name of the field to extract
        data_type: Expected data type (optional, will be inferred from model if not provided)
        documents: List of document texts to extract from

    Returns:
        Extracted field value in the correct data type
    """

    # Get data type from model if not provided
    if data_type is None:
        field_info = ExtractedData.get_field_info()
        if field_name in field_info:
            data_type = field_info[field_name]
        else:
            data_type = "string"  # Default fallback

    # Get the appropriate prompt for the field
    # Convert list of document texts to dict format expected by get_prompt
    documents_dict = {}
    for i, doc_text in enumerate(documents):
        documents_dict[f"document_{i+1}"] = doc_text

    prompt_text = get_prompt(field_name, documents_dict)

    # Define JSON schema based on data type
    json_schema = _get_json_schema_for_field(field_name, data_type)

    # Create the full prompt with schema instructions
    full_prompt = f"""{prompt_text}

Please return your response as valid JSON that follows this exact schema:

{json.dumps(json_schema, indent=2)}

The response must be valid JSON and contain the extracted field value(s)."""

    try:
        # print(f"DEBUG: Sending request to Claude for field '{field_name}'")
        # print(full_prompt)
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0.25,
            messages=[{"role": "user", "content": full_prompt}],
        )

        response_text = response.content[0].text.strip()
        # print(f"DEBUG: Claude response for '{field_name}': {response_text}")

        # Clean up the response text - extract JSON from the response
        json_text = response_text

        # Look for JSON within code blocks first
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            if end != -1:
                json_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            if end != -1:
                json_text = response_text[start:end].strip()
        else:
            # Look for JSON object starting with { and ending with }
            start = response_text.find("{")
            if start != -1:
                # Find the matching closing brace
                brace_count = 0
                for i, char in enumerate(response_text[start:], start):
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            json_text = response_text[start : i + 1]
                            break

        json_text = json_text.strip()
        # print(f"DEBUG: Extracted JSON text for '{field_name}': {json_text}")

        # Parse the JSON response
        parsed_response = json.loads(json_text)
        # print(f"DEBUG: Parsed JSON for '{field_name}': {parsed_response}")

        # Return the extracted value(s)
        result = _extract_value_from_response(parsed_response, field_name, data_type)
        # print(f"DEBUG LLM: Final extracted value for '{field_name}': {result}")
        return result

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response for field '{field_name}': {e}")
        print(f"Raw response: {response_text}")
        return _get_default_value(data_type)
    except Exception as e:
        print(f"Error extracting field '{field_name}': {e}")
        return _get_default_value(data_type)


def _get_json_schema_for_field(field_name: str, data_type: str) -> dict:
    """Generate JSON schema for the field based on its data type."""

    # Map common data types to JSON schema types
    type_mapping = {
        "string": "string",
        "str": "string",
        "text": "string",
        "number": "number",
        "float": "number",
        "integer": "integer",
        "int": "integer",
        "boolean": "boolean",
        "bool": "boolean",
        "array": "array",
        "list": "array",
        "date": "string",  # Dates as ISO strings
        "datetime": "string",  # Datetime as ISO strings
    }

    schema_type = type_mapping.get(data_type.lower(), "string")

    schema = {
        "type": "object",
        "properties": {
            field_name: {"type": schema_type},
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "source_location": {
                "type": "string",
                "description": "Where in the document(s) the value was found",
            },
        },
        "required": [field_name],
    }

    # Add format for dates
    if data_type.lower() in ["date", "datetime"]:
        schema["properties"][field_name]["format"] = "date"
        schema["properties"][field_name]["description"] = "Date in YYYY-MM-DD format"

    # Handle arrays differently
    if schema_type == "array":
        schema["properties"][field_name] = {
            "type": "array",
            "items": {"type": "string"},
        }

    return schema


def _extract_value_from_response(
    parsed_response: dict, field_name: str, data_type: str
) -> Any:
    """Extract and convert the field value to the correct data type."""

    if field_name not in parsed_response:
        return _get_default_value(data_type)

    value = parsed_response[field_name]

    # Handle null/None values
    if (
        value is None
        or value == "Not found"
        or value == "No date found"
        or value == "Unknown"
    ):
        return _get_default_value(data_type)

    # Convert to appropriate type
    try:
        if data_type.lower() in ["integer", "int"]:
            return int(value) if value != "" else None
        elif data_type.lower() in ["number", "float"]:
            return float(value) if value != "" else None
        elif data_type.lower() in ["boolean", "bool"]:
            if isinstance(value, str):
                return value.lower() in ["true", "yes", "1", "on"]
            return bool(value)
        elif data_type.lower() in ["array", "list"]:
            return value if isinstance(value, list) else [value] if value else []
        elif data_type.lower() in ["datetime", "date"]:
            if isinstance(value, str) and value.strip():
                try:
                    # Try to parse ISO format date
                    return datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    # Try common date formats
                    for fmt in [
                        "%Y-%m-%d",
                        "%m/%d/%Y",
                        "%d/%m/%Y",
                        "%Y-%m-%d %H:%M:%S",
                    ]:
                        try:
                            return datetime.strptime(value, fmt)
                        except ValueError:
                            continue
                    return None
            return None
        else:  # string, etc.
            return str(value) if value != "" else None
    except (ValueError, TypeError):
        return _get_default_value(data_type)


def _get_default_value(data_type: str) -> Any:
    """Return default value for a given data type."""
    type_defaults = {
        "string": None,
        "str": None,
        "text": None,
        "number": None,
        "float": None,
        "integer": None,
        "int": None,
        "boolean": False,
        "bool": False,
        "array": [],
        "list": [],
        "date": None,
        "datetime": None,
    }
    return type_defaults.get(data_type.lower(), None)


async def extract_all_fields_from_documents(documents: List[str]) -> ExtractedData:
    """
    Extract all fields from document texts in parallel and return as ExtractedData model.

    Args:
        documents: List of document texts to extract from

    Returns:
        ExtractedData: Model with all extracted fields
    """
    field_info = ExtractedData.get_field_info()

    # Create coroutines for all field extractions
    async def extract_single_field(field_name: str, data_type: str):
        try:
            return field_name, await extract_field_from_documents(
                field_name, data_type, documents
            )
        except Exception as e:
            print(f"ERROR: extracting field '{field_name}': {e}")
            return field_name, _get_default_value(data_type)

    # Create tasks for all fields
    tasks = [
        extract_single_field(field_name, data_type)
        for field_name, data_type in field_info.items()
    ]

    # Execute all extractions in parallel
    results = await asyncio.gather(*tasks)

    # Build the extracted data dictionary
    extracted_data = dict(results)

    return ExtractedData(**extracted_data)
