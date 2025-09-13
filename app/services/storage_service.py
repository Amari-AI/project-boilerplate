import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

class JSONStorageService:
    def __init__(self, storage_file: str = "data_store.json"):
        self.storage_file = storage_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file, create empty structure if file doesn't exist."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Return empty structure
        return {
            "documents": {},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def _save_data(self) -> None:
        """Save current data to JSON file."""
        self.data["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self.storage_file, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)
    
    def find_document_by_file_ids(self, file_ids: List[str]) -> Optional[str]:
        """Find existing document by file IDs from file metadata."""
        for doc_id, doc_data in self.data["documents"].items():
            file_metadata = doc_data.get("file_metadata", [])
            doc_file_ids = {meta.get("file_id") for meta in file_metadata if meta.get("file_id")}
            
            # Check if any of the provided file IDs match existing document file IDs
            if doc_file_ids.intersection(set(file_ids)):
                return doc_id
        return None
    
    def save_document(self, extracted_data: Dict[str, Any], document_texts: Dict[str, Any], file_metadata: List[Dict[str, Any]] = None) -> str:
        """Save a processed document and return its ID."""
        doc_id = str(uuid.uuid4())
        self.data["documents"][doc_id] = {
            "id": doc_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "extracted_data": extracted_data,
            "document_texts": document_texts,
            "file_metadata": file_metadata or []
        }
        self._save_data()
        return doc_id
    
    def update_existing_document(self, doc_id: str, extracted_data: Dict[str, Any], document_texts: Dict[str, Any], file_metadata: List[Dict[str, Any]] = None) -> bool:
        """Update an existing document with new data."""
        if doc_id not in self.data["documents"]:
            return False
        
        # Keep the original created_at timestamp
        original_created_at = self.data["documents"][doc_id].get("created_at")
        
        self.data["documents"][doc_id].update({
            "last_updated": datetime.now().isoformat(),
            "extracted_data": extracted_data,
            "document_texts": document_texts,
            "file_metadata": file_metadata or []
        })
        
        # Preserve the original creation time
        if original_created_at:
            self.data["documents"][doc_id]["created_at"] = original_created_at
            
        self._save_data()
        return True
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve document data by ID."""
        return self.data["documents"].get(doc_id)
    
    def update_document_field(self, doc_id: str, field: str, value: Any) -> bool:
        """Update a specific field in the document's extracted data."""
        if doc_id not in self.data["documents"]:
            return False
        
        if "extracted_data" not in self.data["documents"][doc_id]:
            self.data["documents"][doc_id]["extracted_data"] = {}
        
        self.data["documents"][doc_id]["extracted_data"][field] = value
        self.data["documents"][doc_id]["last_updated"] = datetime.now().isoformat()
        self._save_data()
        return True
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents with basic info."""
        documents = []
        for doc_id, doc_data in self.data["documents"].items():
            # Get original filenames from file metadata
            file_metadata = doc_data.get("file_metadata", [])
            filenames = [meta.get("original_filename", "") for meta in file_metadata if meta.get("original_filename")]
            
            documents.append({
                "id": doc_id,
                "created_at": doc_data.get("created_at"),
                "last_updated": doc_data.get("last_updated"),
                "has_data": bool(doc_data.get("extracted_data")),
                "filenames": filenames,
                "primary_filename": filenames[0] if filenames else None
            })
        return documents
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document."""
        if doc_id in self.data["documents"]:
            del self.data["documents"][doc_id]
            self._save_data()
            return True
        return False
    
    def get_latest_document(self) -> Optional[Dict[str, Any]]:
        """Get the most recently created document."""
        if not self.data["documents"]:
            return None
        
        latest_doc = max(
            self.data["documents"].values(),
            key=lambda x: x.get("created_at", "")
        )
        return latest_doc

# Global instance
storage_service = JSONStorageService()
