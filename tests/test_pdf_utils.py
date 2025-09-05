import pytest
import tempfile
import os
from app.utils.pdf_utils import extract_text_from_pdf


class TestPDFUtils:
    
    def test_extract_text_from_nonexistent_file(self):
        """Test handling of non-existent PDF file"""
        result = extract_text_from_pdf("nonexistent.pdf")
        assert result == ""
    
    def test_extract_text_from_invalid_pdf(self):
        """Test handling of invalid PDF file"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"This is not a PDF file")
            tmp_file_path = tmp_file.name
        
        try:
            result = extract_text_from_pdf(tmp_file_path)
            assert result == ""
        finally:
            os.unlink(tmp_file_path)
    
    def test_extract_text_with_empty_file(self):
        """Test handling of empty PDF file"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file_path = tmp_file.name
        
        try:
            result = extract_text_from_pdf(tmp_file_path)
            assert result == ""
        finally:
            os.unlink(tmp_file_path)
    
    def test_file_path_validation(self):
        """Test that function handles file path correctly"""
        # Test with None
        with pytest.raises((TypeError, AttributeError)):
            extract_text_from_pdf(None)
        
        # Test with empty string
        result = extract_text_from_pdf("")
        assert result == ""