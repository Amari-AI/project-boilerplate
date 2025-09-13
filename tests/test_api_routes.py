import pytest
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
from io import BytesIO

@pytest.mark.api
class TestProcessDocumentsEndpoint:
    """Tests for the /process-documents endpoint."""

    def test_process_documents_success(self, client, sample_pdf_file, mock_llm_service, temp_upload_dir):
        """Test successful document processing."""
        with patch('app.api.routes.UPLOADS_DIR', temp_upload_dir):
            with patch('app.services.document_processor.process_documents') as mock_processor:
                mock_processor.return_value = {"pdf_test.pdf": "Test content"}
                
                with open(sample_pdf_file, 'rb') as f:
                    response = client.post(
                        "/process-documents",
                        files=[("files", ("test.pdf", f, "application/pdf"))]
                    )
                
                assert response.status_code == 200
                data = response.json()
                assert "extracted_data" in data
                assert "document_texts" in data
                assert "file_metadata" in data
                assert data["extracted_data"]["bill_of_lading_number"] == "TEST123"

    def test_process_documents_no_files(self, client):
        """Test processing with no files provided."""
        response = client.post("/process-documents", files=[])
        assert response.status_code == 400
        assert "No files provided" in response.json()["detail"]

    def test_process_documents_invalid_file_type(self, client):
        """Test processing with invalid file type."""
        file_content = b"This is a text file"
        response = client.post(
            "/process-documents",
            files=[("files", ("test.txt", BytesIO(file_content), "text/plain"))]
        )
        assert response.status_code == 400
        assert "File type not allowed" in response.json()["detail"]

    def test_process_documents_valid_file_types(self, client, sample_pdf_file, sample_excel_file, mock_llm_service, temp_upload_dir):
        """Test processing with valid file types (PDF, Excel)."""
        with patch('app.api.routes.UPLOADS_DIR', temp_upload_dir):
            with patch('app.services.document_processor.process_documents') as mock_processor:
                mock_processor.return_value = {"test_files": "content"}
                
                files = []
                with open(sample_pdf_file, 'rb') as f:
                    files.append(("files", ("test.pdf", f.read(), "application/pdf")))
                
                with open(sample_excel_file, 'rb') as f:
                    files.append(("files", ("test.xlsx", f.read(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")))
                
                response = client.post("/process-documents", files=files)
                assert response.status_code == 200

    def test_process_documents_processing_error(self, client, sample_pdf_file, temp_upload_dir):
        """Test handling of processing errors."""
        with patch('app.api.routes.UPLOADS_DIR', temp_upload_dir):
            with patch('app.services.document_processor.process_documents') as mock_processor:
                mock_processor.side_effect = Exception("Processing failed")
                
                with open(sample_pdf_file, 'rb') as f:
                    response = client.post(
                        "/process-documents",
                        files=[("files", ("test.pdf", f, "application/pdf"))]
                    )
                
                assert response.status_code == 500
                assert "Error processing documents" in response.json()["detail"]


@pytest.mark.api
class TestDocumentStorageEndpoints:
    """Tests for document storage endpoints."""

    def test_save_document_success(self, client, temp_storage_service):
        """Test successful document saving."""
        with patch('app.api.routes.storage_service', temp_storage_service):
            document_data = {
                "extracted_data": {"bill_of_lading_number": "TEST123"},
                "document_texts": {"test.pdf": "content"},
                "file_metadata": [{"original_filename": "test.pdf"}]
            }
            
            response = client.post("/documents/save", json=document_data)
            assert response.status_code == 200
            data = response.json()
            assert "document_id" in data
            assert data["message"] == "Document saved successfully"

    def test_save_document_missing_fields(self, client):
        """Test document saving with missing required fields."""
        document_data = {"extracted_data": {"test": "data"}}  # Missing document_texts
        
        response = client.post("/documents/save", json=document_data)
        assert response.status_code == 400
        assert "Missing required fields" in response.json()["detail"]

    def test_get_document_success(self, client, temp_storage_service):
        """Test successful document retrieval."""
        with patch('app.api.routes.storage_service', temp_storage_service):
            # Save a document first
            doc_id = temp_storage_service.save_document(
                {"test": "data"}, 
                {"content": "test"}, 
                [{"filename": "test.pdf"}]
            )
            
            response = client.get(f"/documents/{doc_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == doc_id
            assert "extracted_data" in data

    def test_get_document_not_found(self, client, temp_storage_service):
        """Test document retrieval with non-existent ID."""
        with patch('app.api.routes.storage_service', temp_storage_service):
            response = client.get("/documents/nonexistent-id")
            assert response.status_code == 404
            assert "Document not found" in response.json()["detail"]

    def test_update_document_field_success(self, client, temp_storage_service):
        """Test successful document field update."""
        with patch('app.api.routes.storage_service', temp_storage_service):
            # Save a document first
            doc_id = temp_storage_service.save_document(
                {"bill_of_lading_number": "OLD123"}, 
                {"content": "test"},
                []
            )
            
            field_data = {"field": "bill_of_lading_number", "value": "NEW123"}
            response = client.put(f"/documents/{doc_id}/field", json=field_data)
            
            assert response.status_code == 200
            assert response.json()["message"] == "Field updated successfully"

    def test_update_document_field_missing_data(self, client):
        """Test document field update with missing field/value."""
        field_data = {"field": "test_field"}  # Missing value
        
        response = client.put("/documents/test-id/field", json=field_data)
        assert response.status_code == 400
        assert "Both 'field' and 'value' are required" in response.json()["detail"]

    def test_update_document_field_not_found(self, client, temp_storage_service):
        """Test document field update with non-existent document."""
        with patch('app.api.routes.storage_service', temp_storage_service):
            field_data = {"field": "test_field", "value": "test_value"}
            
            response = client.put("/documents/nonexistent-id/field", json=field_data)
            assert response.status_code == 404
            assert "Document not found" in response.json()["detail"]

    def test_list_documents(self, client, temp_storage_service):
        """Test document listing."""
        with patch('app.api.routes.storage_service', temp_storage_service):
            # Save some documents
            temp_storage_service.save_document({"test1": "data1"}, {"content1": "test1"}, [])
            temp_storage_service.save_document({"test2": "data2"}, {"content2": "test2"}, [])
            
            response = client.get("/documents")
            assert response.status_code == 200
            data = response.json()
            assert "documents" in data
            assert len(data["documents"]) == 2

    def test_get_latest_document(self, client, temp_storage_service):
        """Test getting the latest document."""
        with patch('app.api.routes.storage_service', temp_storage_service):
            # Save a document
            temp_storage_service.save_document({"latest": "data"}, {"content": "test"}, [])
            
            response = client.get("/documents/latest")
            assert response.status_code == 200
            data = response.json()
            assert "extracted_data" in data

    def test_get_latest_document_empty(self, client, temp_storage_service):
        """Test getting latest document when no documents exist."""
        with patch('app.api.routes.storage_service', temp_storage_service):
            response = client.get("/documents/latest")
            assert response.status_code == 404
            assert "No documents found" in response.json()["detail"]

    def test_delete_document_success(self, client, temp_storage_service):
        """Test successful document deletion."""
        with patch('app.api.routes.storage_service', temp_storage_service):
            # Save a document first
            doc_id = temp_storage_service.save_document({"test": "data"}, {"content": "test"}, [])
            
            response = client.delete(f"/documents/{doc_id}")
            assert response.status_code == 200
            assert response.json()["message"] == "Document deleted successfully"

    def test_delete_document_not_found(self, client, temp_storage_service):
        """Test document deletion with non-existent ID."""
        with patch('app.api.routes.storage_service', temp_storage_service):
            response = client.delete("/documents/nonexistent-id")
            assert response.status_code == 404
            assert "Document not found" in response.json()["detail"]

    def test_save_document_update_existing(self, client, temp_storage_service):
        """Test that saving a document with existing file ID updates instead of creating new."""
        with patch('app.api.routes.storage_service', temp_storage_service):
            # First save
            document_data = {
                "extracted_data": {"bill_of_lading_number": "BOL123"},
                "document_texts": {"content": "test"},
                "file_metadata": [{"file_id": "test-file-123", "original_filename": "test.pdf"}]
            }
            
            response1 = client.post("/documents/save", json=document_data)
            assert response1.status_code == 200
            data1 = response1.json()
            assert data1["action"] == "created"
            original_doc_id = data1["document_id"]
            
            # Save again with same file ID - should update
            document_data["extracted_data"]["bill_of_lading_number"] = "BOL456"  # Changed data
            document_data["extracted_data"]["new_field"] = "new_value"  # Added field
            
            response2 = client.post("/documents/save", json=document_data)
            assert response2.status_code == 200
            data2 = response2.json()
            assert data2["action"] == "updated"
            assert data2["document_id"] == original_doc_id  # Same document ID
            
            # Verify the update
            get_response = client.get(f"/documents/{original_doc_id}")
            assert get_response.status_code == 200
            updated_doc = get_response.json()
            assert updated_doc["extracted_data"]["bill_of_lading_number"] == "BOL456"
            assert updated_doc["extracted_data"]["new_field"] == "new_value"


@pytest.mark.api
class TestFileServingEndpoints:
    """Tests for file serving endpoints."""

    def test_serve_file_success(self, client, temp_upload_dir, temp_storage_service):
        """Test successful file serving."""
        # Create a test file
        test_file = temp_upload_dir / "test.pdf"
        test_file.write_text("Test PDF content")
        
        with patch('app.api.routes.UPLOADS_DIR', temp_upload_dir):
            with patch('app.api.routes.storage_service', temp_storage_service):
                response = client.get("/files/test.pdf")
                assert response.status_code == 200
                assert response.headers["content-disposition"] == "inline"

    def test_serve_file_download(self, client, temp_upload_dir, temp_storage_service):
        """Test file serving with download parameter."""
        # Create a test file
        test_file = temp_upload_dir / "test.pdf"
        test_file.write_text("Test PDF content")
        
        # Add file metadata to storage service
        temp_storage_service.save_document(
            {"test": "data"},
            {"content": "test"},
            [{"saved_filename": "test.pdf", "original_filename": "original.pdf"}]
        )
        
        with patch('app.api.routes.UPLOADS_DIR', temp_upload_dir):
            with patch('app.api.routes.storage_service', temp_storage_service):
                response = client.get("/files/test.pdf?download=true")
                assert response.status_code == 200
                assert 'attachment; filename="original.pdf"' in response.headers["content-disposition"]

    def test_serve_file_not_found(self, client, temp_upload_dir):
        """Test file serving with non-existent file."""
        with patch('app.api.routes.UPLOADS_DIR', temp_upload_dir):
            response = client.get("/files/nonexistent.pdf")
            assert response.status_code == 404
            assert "File not found" in response.json()["detail"]

    def test_serve_file_media_types(self, client, temp_upload_dir, temp_storage_service):
        """Test file serving with different media types."""
        files_and_types = [
            ("test.pdf", "application/pdf"),
            ("test.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            ("test.txt", "application/octet-stream")
        ]
        
        with patch('app.api.routes.UPLOADS_DIR', temp_upload_dir):
            with patch('app.api.routes.storage_service', temp_storage_service):
                for filename, expected_type in files_and_types:
                    # Create test file
                    test_file = temp_upload_dir / filename
                    test_file.write_text("Test content")
                    
                    response = client.get(f"/files/{filename}")
                    assert response.status_code == 200
                    # Note: FastAPI TestClient might not preserve exact media type headers

    def test_serve_parsed_excel_success(self, client, temp_upload_dir, sample_excel_file):
        """Test successful Excel file parsing."""
        # Copy sample Excel file to uploads directory
        import shutil
        excel_filename = "test.xlsx"
        dest_path = temp_upload_dir / excel_filename
        shutil.copy2(sample_excel_file, dest_path)
        
        with patch('app.api.routes.UPLOADS_DIR', temp_upload_dir):
            response = client.get(f"/files/{excel_filename}/parsed")
            assert response.status_code == 200
            data = response.json()
            assert "sheets" in data

    def test_serve_parsed_excel_file_not_found(self, client, temp_upload_dir):
        """Test Excel parsing with non-existent file."""
        with patch('app.api.routes.UPLOADS_DIR', temp_upload_dir):
            response = client.get("/files/nonexistent.xlsx/parsed")
            assert response.status_code == 404
            assert "File not found" in response.json()["detail"]

    def test_serve_parsed_excel_not_excel_file(self, client, temp_upload_dir):
        """Test Excel parsing with non-Excel file."""
        # Create a non-Excel file
        test_file = temp_upload_dir / "test.txt"
        test_file.write_text("This is not an Excel file")
        
        with patch('app.api.routes.UPLOADS_DIR', temp_upload_dir):
            response = client.get("/files/test.txt/parsed")
            assert response.status_code == 400
            assert "File is not an Excel file" in response.json()["detail"]

    def test_serve_parsed_excel_parsing_error(self, client, temp_upload_dir):
        """Test Excel parsing with corrupted Excel file."""
        # Create a corrupted Excel file
        test_file = temp_upload_dir / "corrupted.xlsx"
        test_file.write_text("Not a valid Excel file")
        
        with patch('app.api.routes.UPLOADS_DIR', temp_upload_dir):
            response = client.get("/files/corrupted.xlsx/parsed")
            assert response.status_code == 500
            assert "Error parsing Excel file" in response.json()["detail"]


@pytest.mark.integration
class TestIntegrationScenarios:
    """Integration tests covering complete workflows."""

    def test_complete_document_workflow(self, client, sample_pdf_file, mock_llm_service, temp_upload_dir, temp_storage_service):
        """Test complete workflow: process -> save -> retrieve -> update -> delete."""
        with patch('app.api.routes.UPLOADS_DIR', temp_upload_dir):
            with patch('app.api.routes.storage_service', temp_storage_service):
                with patch('app.services.document_processor.process_documents') as mock_processor:
                    mock_processor.return_value = {"pdf_test.pdf": "Test content"}
                    
                    # 1. Process document
                    with open(sample_pdf_file, 'rb') as f:
                        process_response = client.post(
                            "/process-documents",
                            files=[("files", ("test.pdf", f, "application/pdf"))]
                        )
                    assert process_response.status_code == 200
                    
                    # 2. Save document
                    save_data = process_response.json()
                    save_response = client.post("/documents/save", json=save_data)
                    assert save_response.status_code == 200
                    doc_id = save_response.json()["document_id"]
                    
                    # 3. Retrieve document
                    get_response = client.get(f"/documents/{doc_id}")
                    assert get_response.status_code == 200
                    
                    # 4. Update document field
                    update_data = {"field": "bill_of_lading_number", "value": "UPDATED123"}
                    update_response = client.put(f"/documents/{doc_id}/field", json=update_data)
                    assert update_response.status_code == 200
                    
                    # 5. Delete document
                    delete_response = client.delete(f"/documents/{doc_id}")
                    assert delete_response.status_code == 200

    def test_file_upload_and_serving(self, client, sample_pdf_file, temp_upload_dir, temp_storage_service):
        """Test file upload and subsequent serving."""
        with patch('app.api.routes.UPLOADS_DIR', temp_upload_dir):
            with patch('app.api.routes.storage_service', temp_storage_service):
                with patch('app.services.document_processor.process_documents') as mock_processor:
                    with patch('app.services.llm_service.extract_field_from_document') as mock_llm:
                        mock_processor.return_value = {"pdf_test.pdf": "Test content"}
                        mock_llm.return_value = {"bill_of_lading_number": "TEST123"}
                        
                        # Process and save file
                        with open(sample_pdf_file, 'rb') as f:
                            process_response = client.post(
                                "/process-documents",
                                files=[("files", ("test.pdf", f, "application/pdf"))]
                            )
                        
                        # Get the saved filename from response
                        file_metadata = process_response.json()["file_metadata"]
                        saved_filename = file_metadata[0]["saved_filename"]
                        
                        # Test file serving
                        serve_response = client.get(f"/files/{saved_filename}")
                        assert serve_response.status_code == 200