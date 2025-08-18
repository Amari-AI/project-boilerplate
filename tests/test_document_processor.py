import pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from app.services.document_processor import process_documents


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


class TestDocumentProcessor:
    """Test class for document processing functionality"""

    def test_process_documents_basic_functionality(self):
        """Test basic document processing without LLM extraction"""
        sample_files = [
            str(Path("data/sample_bill_of_lading.pdf")),
            str(Path("data/sample_invoice.xlsx")),
        ]

        # Verify files exist
        for file_path in sample_files:
            assert Path(file_path).exists(), f"Sample file not found: {file_path}"

        # Process documents
        result = process_documents(sample_files)

        # Basic structure assertions
        assert isinstance(result, dict), "Result should be a dictionary"
        assert len(result) > 0, "Result should not be empty"

        # Check that text was extracted
        if "pdf_text" in result:
            assert isinstance(result["pdf_text"], str), "PDF text should be a string"
            assert len(result["pdf_text"]) > 0, "PDF text should not be empty"

        if "excel_text" in result:
            assert isinstance(
                result["excel_text"], str
            ), "Excel text should be a string"
            assert len(result["excel_text"]) > 0, "Excel text should not be empty"

    def test_process_documents_pdf_only(self):
        """Test processing PDF file only"""
        sample_files = [str(Path("data/sample_bill_of_lading.pdf"))]

        # Verify file exists
        assert Path(
            sample_files[0]
        ).exists(), f"Sample file not found: {sample_files[0]}"

        result = process_documents(sample_files)

        # Should contain PDF text but not Excel text
        assert "pdf_text" in result, "Result should contain pdf_text"
        assert "excel_text" not in result, "Result should not contain excel_text"
        assert len(result["pdf_text"]) > 0, "PDF text should not be empty"

    def test_process_documents_excel_only(self):
        """Test processing Excel file only"""
        sample_files = [str(Path("data/sample_invoice.xlsx"))]

        # Verify file exists
        assert Path(
            sample_files[0]
        ).exists(), f"Sample file not found: {sample_files[0]}"

        result = process_documents(sample_files)

        # Should contain Excel text but not PDF text
        assert "excel_text" in result, "Result should contain excel_text"
        assert "pdf_text" not in result, "Result should not contain pdf_text"
        assert len(result["excel_text"]) > 0, "Excel text should not be empty"

    def test_process_documents_unsupported_file_type(self):
        """Test handling of unsupported file types"""
        # Create a temporary file with unsupported extension
        temp_file = Path("temp_test_file.txt")
        temp_file.write_text("This is a test file")

        try:
            result = process_documents([str(temp_file)])
            # Should return empty dict for unsupported file types
            assert result == {}, "Unsupported files should return empty dict"
        finally:
            # Clean up
            if temp_file.exists():
                temp_file.unlink()

    def test_normalize_value_function(self):
        """Test the value normalization function"""
        # Test None values
        assert normalize_value(None, "string") is None

        # Test string values
        assert normalize_value("test", "string") == "test"

        # Test datetime normalization
        date_string = "2019-08-22T00:00:00Z"
        normalized = normalize_value(date_string, "datetime")
        assert normalized == "2019-08-22"

        # Test non-datetime values
        assert normalize_value("test", "string") == "test"
        assert normalize_value(123, "integer") == 123
