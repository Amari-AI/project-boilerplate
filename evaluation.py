import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import sys

# Import the service functions directly instead of using API calls
from app.services.document_processor import process_documents
from app.services.llm_service import extract_all_fields_from_documents


def get_expected_data() -> Dict[str, Dict[str, Any]]:
    """
    Define expected extraction results for each sample file.
    Based on manual inspection of the sample documents.
    """
    return {
        "sample_bill_of_lading.pdf": {
            "bill_of_lading_number": "ZMLU34110002",
            "container_number": "MSCU1234567",
            "consignee_name": "KABOFER TRADING INC",
            "consignee": "KABOFER TRADING INC",
            "date": "2019-08-22",
            "line_items_count": 1,
            "average_gross_weight": 16250.0,
            "average_price": None,
        },
        "sample_invoice.xlsx": {
            "bill_of_lading_number": None,
            "container_number": None,
            "consignee_name": None,
            "consignee": None,
            "date": None,
            "line_items_count": None,
            "average_gross_weight": None,
            "average_price": None,
        },
    }


async def process_documents_directly(file_paths: list) -> Optional[Dict[str, Any]]:
    """
    Process documents directly using the service functions instead of API calls.

    Args:
        file_paths: List of file paths to process

    Returns:
        Dictionary with extracted data or None if error
    """
    try:
        # Validate file types
        for file_path in file_paths:
            if not file_path.lower().endswith((".pdf", ".xlsx", ".xls")):
                print(
                    f"Unsupported file type: {file_path}. Only PDF, XLS, and XLSX files are supported."
                )
                return None

        # Process documents to extract text
        document_data = process_documents(file_paths)

        # Convert document data to list of text strings (same as API logic)
        document_texts = []
        if "pdf_text" in document_data and document_data["pdf_text"]:
            document_texts.append(document_data["pdf_text"])
        if "excel_text" in document_data and document_data["excel_text"]:
            document_texts.append(document_data["excel_text"])

        if not document_texts:
            print("No text could be extracted from the documents")
            return None

        # Extract structured data using LLM
        extracted_data = await extract_all_fields_from_documents(document_texts)

        # Convert ExtractedData model to dict and return in same format as API
        return {"extracted_data": extracted_data.model_dump()}

    except Exception as e:
        print(f"Error processing documents: {e}")
        return None


def normalize_value(value: Any, expected_type: str) -> Any:
    """
    Normalize values for comparison (handle type conversions, etc.)
    """
    if value is None:
        return None

    if expected_type == "datetime" and isinstance(value, str):
        try:
            # Try to parse datetime string to date only for comparison
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt.date().isoformat()
        except:
            return value

    return value


def compare_fields(expected: Dict[str, Any], actual: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare individual fields between expected and actual data.

    Returns:
        Dictionary with field-by-field comparison results
    """
    results = {}
    all_fields = set(expected.keys()) | set(actual.keys())

    for field in all_fields:
        expected_val = expected.get(field)
        actual_val = actual.get(field)

        # Normalize values for comparison
        expected_norm = normalize_value(expected_val, type(expected_val).__name__)
        actual_norm = normalize_value(actual_val, type(actual_val).__name__)

        is_match = expected_norm == actual_norm
        results[field] = {
            "expected": expected_val,
            "actual": actual_val,
            "match": is_match,
        }

    return results


def evaluate_results(
    expected_data: Dict[str, Any], actual_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate accuracy metrics by comparing expected vs actual results.

    Args:
        expected_data: Dictionary with expected values per file
        actual_data: Dictionary with actual API response

    Returns:
        Dictionary with evaluation metrics
    """
    if not actual_data:
        return {
            "total_accuracy": 0.0,
            "field_accuracy": {},
            "error": "No actual data to compare",
        }

    # For now, we'll evaluate against the first file's expected data
    # In a more complete implementation, we'd need to handle multiple files
    first_file = list(expected_data.keys())[0]
    expected = expected_data[first_file]

    field_comparisons = compare_fields(expected, actual_data)

    # Calculate accuracy metrics
    total_fields = len(field_comparisons)
    correct_fields = sum(1 for comp in field_comparisons.values() if comp["match"])

    field_accuracy = {}
    for field, comp in field_comparisons.items():
        field_accuracy[field] = {
            "accuracy": 1.0 if comp["match"] else 0.0,
            "expected": comp["expected"],
            "actual": comp["actual"],
        }

    return {
        "total_accuracy": correct_fields / total_fields if total_fields > 0 else 0.0,
        "correct_fields": correct_fields,
        "total_fields": total_fields,
        "field_accuracy": field_accuracy,
        "field_comparisons": field_comparisons,
    }


async def main():
    """Main evaluation logic"""
    data_dir = Path("data")

    if not data_dir.exists():
        print("Error: data/ directory not found")
        sys.exit(1)

    # Get sample files
    sample_files = [
        data_dir / "sample_bill_of_lading.pdf",
        data_dir / "sample_invoice.xlsx",
    ]

    missing_files = [f for f in sample_files if not f.exists()]
    if missing_files:
        print(f"Error: Missing sample files: {missing_files}")
        sys.exit(1)

    print("Running document processing evaluation...")
    print("=" * 50)

    # Get expected results
    expected_data = get_expected_data()

    # Test each file individually first
    for file_path in sample_files:
        print(f"\nTesting: {file_path.name}")
        print("-" * 30)

        # Process documents directly
        actual_data = await process_documents_directly([str(file_path)])

        if actual_data is None:
            print("FAIL: Document processing failed")
            continue

        # Evaluate results (handle nested response structure)
        extracted_data = actual_data.get("extracted_data", actual_data)
        expected_for_file = {file_path.name: expected_data[file_path.name]}
        metrics = evaluate_results(expected_for_file, extracted_data)

        # Print results
        print(f"Overall Accuracy: {metrics['total_accuracy']:.2%}")
        print(f"Correct Fields: {metrics['correct_fields']}/{metrics['total_fields']}")

        print("\nField-by-field results:")
        for field, accuracy_info in metrics["field_accuracy"].items():
            status = "PASS" if accuracy_info["accuracy"] == 1.0 else "FAIL"
            print(
                f"  {status} {field}: {accuracy_info['expected']} → {accuracy_info['actual']}"
            )

    # Test with both files together
    print(f"\n\nTesting: Both files together")
    print("-" * 30)

    actual_data = await process_documents_directly([str(f) for f in sample_files])
    if actual_data:
        # Handle nested response structure
        extracted_data = actual_data.get("extracted_data", actual_data)
        # Use first file's expected data for combined test
        first_file = sample_files[0].name
        expected_for_combined = {first_file: expected_data[first_file]}
        metrics = evaluate_results(expected_for_combined, extracted_data)

        print(f"Overall Accuracy: {metrics['total_accuracy']:.2%}")
        print(f"Correct Fields: {metrics['correct_fields']}/{metrics['total_fields']}")

        print("\nField-by-field results:")
        for field, accuracy_info in metrics["field_accuracy"].items():
            status = "PASS" if accuracy_info["accuracy"] == 1.0 else "FAIL"
            print(
                f"  {status} {field}: {accuracy_info['expected']} → {accuracy_info['actual']}"
            )
    else:
        print("FAIL: Combined document processing failed")

    print("\n" + "=" * 50)
    print("Evaluation complete!")


if __name__ == "__main__":
    asyncio.run(main())
