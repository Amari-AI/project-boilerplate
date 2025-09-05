import pytest
import tempfile
import os
from app.services.document_processor import process_documents
from pathlib import Path


class TestDocumentProcessor:
    
    def test_process_documents_empty_list(self):
        """Test processing with empty file list"""
        result = process_documents([])
        assert isinstance(result, dict)
        assert "combined_text" in result
        assert result["combined_text"] == ""
    
    def test_process_documents_nonexistent_files(self):
        """Test processing with non-existent files"""
        result = process_documents(["nonexistent.pdf", "missing.xlsx"])
        assert isinstance(result, dict)
        assert "combined_text" in result
        assert "pdf_nonexistent.pdf" in result
        assert "excel_missing.xlsx" in result
    
    def test_process_documents_mixed_valid_invalid(self):
        """Test processing with mix of valid and invalid file paths"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%%EOF")
            tmp_file_path = tmp_file.name
        
        try:
            result = process_documents([tmp_file_path, "nonexistent.xlsx"])
            assert isinstance(result, dict)
            assert "combined_text" in result
            # Check that both files are processed (even if they fail)
            filename = os.path.basename(tmp_file_path)
            assert f"pdf_{filename}" in result
            assert "excel_nonexistent.xlsx" in result
        finally:
            os.unlink(tmp_file_path)
    
    def test_process_documents_return_structure(self):
        """Test that process_documents returns expected structure"""
        result = process_documents([])
        assert isinstance(result, dict)
        
        # Should have combined_text key
        assert "combined_text" in result
