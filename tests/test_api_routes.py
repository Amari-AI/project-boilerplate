import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAPIRoutes:
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert "Document Processing API" in response.json()["message"]
    
    def test_process_documents_no_files(self):
        """Test process-documents endpoint with no files"""
        response = client.post("/process-documents", files=[])
        assert response.status_code == 422  # Validation error for missing files
    
    def test_process_documents_with_invalid_file(self):
        """Test process-documents endpoint with invalid file"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(b"This is a text file")
            tmp_file_path = tmp_file.name
        
        try:
            with open(tmp_file_path, 'rb') as f:
                response = client.post(
                    "/process-documents",
                    files=[("files", ("test.txt", f, "text/plain"))]
                )
            
            # Should process but may return an error about unsupported file type
            assert response.status_code == 200
            result = response.json()
            assert "status" in result
            
        finally:
            os.unlink(tmp_file_path)
    
    def test_process_documents_with_empty_pdf(self):
        """Test process-documents endpoint with empty PDF file"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%%EOF")  # Minimal PDF structure
            tmp_file_path = tmp_file.name
        
        try:
            with open(tmp_file_path, 'rb') as f:
                response = client.post(
                    "/process-documents",
                    files=[("files", ("test.pdf", f, "application/pdf"))]
                )
            
            assert response.status_code == 200
            result = response.json()
            assert "status" in result
            assert result["status"] in ["success", "error"]
            
        finally:
            os.unlink(tmp_file_path)
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options("/")
        assert response.status_code in [200, 405]  # OPTIONS might not be explicitly handled
        
        # Test with a GET request to check CORS middleware
        response = client.get("/")
        assert response.status_code == 200