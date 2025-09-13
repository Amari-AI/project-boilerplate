import pytest
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

from app.services.storage_service import JSONStorageService


@pytest.mark.storage
class TestJSONStorageService:
    """Tests for the JSONStorageService class."""

    def test_init_new_storage_file(self):
        """Test initialization with a new storage file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = f.name
        
        try:
            # Remove the file to test creation
            os.unlink(temp_file)
            
            service = JSONStorageService(temp_file)
            
            assert service.storage_file == temp_file
            assert "documents" in service.data
            assert "metadata" in service.data
            assert service.data["documents"] == {}
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_init_existing_storage_file(self):
        """Test initialization with an existing storage file."""
        test_data = {
            "documents": {"test-id": {"test": "data"}},
            "metadata": {"created_at": "2023-01-01T00:00:00"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            service = JSONStorageService(temp_file)
            
            assert service.data["documents"]["test-id"]["test"] == "data"
            
        finally:
            os.unlink(temp_file)

    def test_init_corrupted_storage_file(self):
        """Test initialization with a corrupted storage file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name
        
        try:
            service = JSONStorageService(temp_file)
            
            # Should create new empty structure
            assert service.data["documents"] == {}
            assert "metadata" in service.data
            
        finally:
            os.unlink(temp_file)

    def test_save_document(self, temp_storage_service):
        """Test saving a document."""
        extracted_data = {"bill_of_lading_number": "TEST123"}
        document_texts = {"test.pdf": "content"}
        file_metadata = [{"original_filename": "test.pdf"}]
        
        doc_id = temp_storage_service.save_document(
            extracted_data, document_texts, file_metadata
        )
        
        assert doc_id is not None
        assert doc_id in temp_storage_service.data["documents"]
        
        doc = temp_storage_service.data["documents"][doc_id]
        assert doc["extracted_data"] == extracted_data
        assert doc["document_texts"] == document_texts
        assert doc["file_metadata"] == file_metadata
        assert "created_at" in doc
        assert "last_updated" in doc

    def test_save_document_without_metadata(self, temp_storage_service):
        """Test saving a document without file metadata."""
        extracted_data = {"test": "data"}
        document_texts = {"content": "test"}
        
        doc_id = temp_storage_service.save_document(extracted_data, document_texts)
        
        doc = temp_storage_service.data["documents"][doc_id]
        assert doc["file_metadata"] == []

    def test_get_document(self, temp_storage_service):
        """Test retrieving a document."""
        doc_id = temp_storage_service.save_document(
            {"test": "data"}, {"content": "test"}
        )
        
        retrieved_doc = temp_storage_service.get_document(doc_id)
        
        assert retrieved_doc is not None
        assert retrieved_doc["id"] == doc_id
        assert retrieved_doc["extracted_data"]["test"] == "data"

    def test_get_nonexistent_document(self, temp_storage_service):
        """Test retrieving a non-existent document."""
        result = temp_storage_service.get_document("nonexistent-id")
        assert result is None

    def test_update_document_field(self, temp_storage_service):
        """Test updating a document field."""
        doc_id = temp_storage_service.save_document(
            {"bill_of_lading_number": "OLD123"}, {"content": "test"}
        )
        
        success = temp_storage_service.update_document_field(
            doc_id, "bill_of_lading_number", "NEW123"
        )
        
        assert success is True
        
        doc = temp_storage_service.get_document(doc_id)
        assert doc["extracted_data"]["bill_of_lading_number"] == "NEW123"

    def test_update_document_field_new_field(self, temp_storage_service):
        """Test updating a document with a new field."""
        doc_id = temp_storage_service.save_document(
            {"existing": "data"}, {"content": "test"}
        )
        
        success = temp_storage_service.update_document_field(
            doc_id, "new_field", "new_value"
        )
        
        assert success is True
        
        doc = temp_storage_service.get_document(doc_id)
        assert doc["extracted_data"]["new_field"] == "new_value"
        assert doc["extracted_data"]["existing"] == "data"

    def test_update_nonexistent_document_field(self, temp_storage_service):
        """Test updating a field in a non-existent document."""
        success = temp_storage_service.update_document_field(
            "nonexistent-id", "field", "value"
        )
        
        assert success is False

    def test_list_documents_empty(self, temp_storage_service):
        """Test listing documents when storage is empty."""
        documents = temp_storage_service.list_documents()
        
        assert documents == []

    def test_list_documents_with_data(self, temp_storage_service):
        """Test listing documents with data."""
        # Save some documents
        doc_id1 = temp_storage_service.save_document(
            {"test1": "data1"}, {"content1": "test1"}, 
            [{"original_filename": "file1.pdf"}]
        )
        doc_id2 = temp_storage_service.save_document(
            {"test2": "data2"}, {"content2": "test2"}, 
            [{"original_filename": "file2.pdf"}]
        )
        
        documents = temp_storage_service.list_documents()
        
        assert len(documents) == 2
        
        # Check structure
        for doc in documents:
            assert "id" in doc
            assert "created_at" in doc
            assert "last_updated" in doc
            assert "has_data" in doc
            assert "filenames" in doc
            assert "primary_filename" in doc
            
        # Check specific data
        doc_ids = [doc["id"] for doc in documents]
        assert doc_id1 in doc_ids
        assert doc_id2 in doc_ids
        
        # Check filename extraction
        filenames = [doc["primary_filename"] for doc in documents]
        assert "file1.pdf" in filenames
        assert "file2.pdf" in filenames

    def test_list_documents_multiple_files(self, temp_storage_service):
        """Test listing documents with multiple files."""
        doc_id = temp_storage_service.save_document(
            {"test": "data"}, {"content": "test"},
            [
                {"original_filename": "file1.pdf"},
                {"original_filename": "file2.xlsx"}
            ]
        )
        
        documents = temp_storage_service.list_documents()
        
        assert len(documents) == 1
        doc = documents[0]
        assert len(doc["filenames"]) == 2
        assert "file1.pdf" in doc["filenames"]
        assert "file2.xlsx" in doc["filenames"]
        assert doc["primary_filename"] == "file1.pdf"

    def test_delete_document(self, temp_storage_service):
        """Test deleting a document."""
        doc_id = temp_storage_service.save_document(
            {"test": "data"}, {"content": "test"}
        )
        
        # Verify document exists
        assert temp_storage_service.get_document(doc_id) is not None
        
        success = temp_storage_service.delete_document(doc_id)
        
        assert success is True
        assert temp_storage_service.get_document(doc_id) is None

    def test_delete_nonexistent_document(self, temp_storage_service):
        """Test deleting a non-existent document."""
        success = temp_storage_service.delete_document("nonexistent-id")
        assert success is False

    def test_get_latest_document(self, temp_storage_service):
        """Test getting the latest document."""
        import time
        
        # Save first document
        doc_id1 = temp_storage_service.save_document(
            {"first": "document"}, {"content": "test1"}
        )
        
        time.sleep(0.01)  # Ensure different timestamps
        
        # Save second document  
        doc_id2 = temp_storage_service.save_document(
            {"second": "document"}, {"content": "test2"}
        )
        
        latest = temp_storage_service.get_latest_document()
        
        assert latest is not None
        assert latest["id"] == doc_id2
        assert latest["extracted_data"]["second"] == "document"

    def test_get_latest_document_empty(self, temp_storage_service):
        """Test getting latest document when storage is empty."""
        latest = temp_storage_service.get_latest_document()
        assert latest is None

    def test_data_persistence(self):
        """Test that data persists across service instances."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = f.name
        
        try:
            # Create first service instance and save data
            service1 = JSONStorageService(temp_file)
            doc_id = service1.save_document(
                {"persistent": "data"}, {"content": "test"}
            )
            
            # Create second service instance
            service2 = JSONStorageService(temp_file)
            
            # Verify data persisted
            doc = service2.get_document(doc_id)
            assert doc is not None
            assert doc["extracted_data"]["persistent"] == "data"
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_concurrent_access(self):
        """Test concurrent access to storage (basic test)."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = f.name
        
        try:
            service1 = JSONStorageService(temp_file)
            service2 = JSONStorageService(temp_file)
            
            # Save from first service
            doc_id1 = service1.save_document(
                {"service1": "data"}, {"content": "test1"}
            )
            
            # Save from second service
            doc_id2 = service2.save_document(
                {"service2": "data"}, {"content": "test2"}
            )
            
            # Both should be able to read their own data
            assert service1.get_document(doc_id1) is not None
            assert service2.get_document(doc_id2) is not None
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_metadata_updates(self, temp_storage_service):
        """Test that metadata is updated properly."""
        initial_updated = temp_storage_service.data["metadata"]["last_updated"]
        
        import time
        time.sleep(0.01)
        
        # Save a document
        temp_storage_service.save_document({"test": "data"}, {"content": "test"})
        
        final_updated = temp_storage_service.data["metadata"]["last_updated"]
        
        assert final_updated != initial_updated

    def test_find_document_by_file_ids(self, temp_storage_service):
        """Test finding documents by file IDs."""
        # Save a document with file metadata
        file_metadata = [{"file_id": "test-file-123", "original_filename": "test.pdf"}]
        doc_id = temp_storage_service.save_document(
            {"test": "data"}, {"content": "test"}, file_metadata
        )
        
        # Should find the document by file ID
        found_doc_id = temp_storage_service.find_document_by_file_ids(["test-file-123"])
        assert found_doc_id == doc_id
        
        # Should not find with different file ID
        not_found = temp_storage_service.find_document_by_file_ids(["different-file-456"])
        assert not_found is None
        
        # Should find with multiple file IDs (one matching)
        found_doc_id = temp_storage_service.find_document_by_file_ids(["wrong-id", "test-file-123"])
        assert found_doc_id == doc_id

    def test_update_existing_document(self, temp_storage_service):
        """Test updating an existing document."""
        # Create initial document
        initial_metadata = [{"file_id": "test-123", "original_filename": "test.pdf"}]
        doc_id = temp_storage_service.save_document(
            {"initial": "data"}, {"content": "initial"}, initial_metadata
        )
        
        initial_doc = temp_storage_service.get_document(doc_id)
        original_created_at = initial_doc["created_at"]
        
        import time
        time.sleep(0.01)
        
        # Update the document
        updated_metadata = [{"file_id": "test-123", "original_filename": "test.pdf", "version": "2"}]
        success = temp_storage_service.update_existing_document(
            doc_id,
            {"updated": "data", "new_field": "value"},
            {"content": "updated"},
            updated_metadata
        )
        
        assert success is True
        
        # Verify the update
        updated_doc = temp_storage_service.get_document(doc_id)
        assert updated_doc["extracted_data"]["updated"] == "data"
        assert updated_doc["extracted_data"]["new_field"] == "value"
        assert "initial" not in updated_doc["extracted_data"]  # Should be completely replaced
        assert updated_doc["document_texts"]["content"] == "updated"
        assert updated_doc["file_metadata"][0]["version"] == "2"
        
        # Should preserve original creation time but update last_updated
        assert updated_doc["created_at"] == original_created_at
        assert updated_doc["last_updated"] != original_created_at

    def test_update_nonexistent_document(self, temp_storage_service):
        """Test updating a document that doesn't exist."""
        success = temp_storage_service.update_existing_document(
            "nonexistent-id",
            {"test": "data"},
            {"content": "test"},
            []
        )
        assert success is False