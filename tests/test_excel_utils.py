import pytest
import tempfile
import os
from openpyxl import Workbook
from app.utils.excel_utils import extract_data_from_excel, format_excel_data_for_llm


class TestExcelUtils:
    
    def create_sample_xlsx(self, data):
        """Helper method to create sample XLSX file"""
        wb = Workbook()
        ws = wb.active
        
        for row_idx, row_data in enumerate(data, 1):
            for col_idx, cell_value in enumerate(row_data, 1):
                ws.cell(row=row_idx, column=col_idx, value=cell_value)
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            wb.save(tmp_file.name)
            return tmp_file.name
    
    def test_extract_data_from_simple_excel(self):
        """Test extraction from simple Excel file"""
        data = [
            ["Name", "Age", "City"],
            ["John", 25, "NYC"],
            ["Jane", 30, "LA"]
        ]
        
        file_path = self.create_sample_xlsx(data)
        try:
            result = extract_data_from_excel(file_path)
            assert isinstance(result, dict)
            assert "Sheet" in str(result) or "sheets" in result
        finally:
            os.unlink(file_path)
    
    def test_extract_data_from_nonexistent_file(self):
        """Test handling of non-existent Excel file"""
        result = extract_data_from_excel("nonexistent.xlsx")
        assert isinstance(result, dict)
        # Should handle gracefully without crashing
    
    def test_format_excel_data_for_llm(self):
        """Test formatting Excel data for LLM processing"""
        sample_data = {
            "Sheet1": [
                ["Header1", "Header2"],
                ["Value1", "Value2"]
            ]
        }
        
        result = format_excel_data_for_llm(sample_data)
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Header1" in result or "Value1" in result
    
    def test_format_empty_excel_data(self):
        """Test formatting empty Excel data"""
        result = format_excel_data_for_llm({})
        assert isinstance(result, str)
        # Empty data returns empty string, which is expected behavior
        assert result == ""
    
    def test_extract_data_from_invalid_file(self):
        """Test handling of invalid Excel file"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            tmp_file.write(b"This is not an Excel file")
            tmp_file_path = tmp_file.name
        
        try:
            result = extract_data_from_excel(tmp_file_path)
            assert isinstance(result, dict)
            # Should handle gracefully without crashing
        finally:
            os.unlink(tmp_file_path)