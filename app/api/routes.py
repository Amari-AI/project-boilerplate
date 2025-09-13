from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Dict, Any
import os
import tempfile
import shutil
from pathlib import Path

from app.services.document_processor import process_documents
from app.services.llm_service import extract_field_from_document
from app.services.storage_service import storage_service
from app.models.shipment import ProcessDocumentsResponse
from app.utils.accuracy_calculator import AccuracyCalculator

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

@router.post("/process-documents")
async def process_documents_endpoint(
    files: List[UploadFile] = File(...),
    ground_truth: Dict[str, Any] = None
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Check file types
    allowed_extensions = {'.pdf', '.xlsx', '.xls'}
    for file in files:
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(status_code=400, detail=f"File type not allowed: {file.filename}")
    
    saved_file_paths = []
    file_metadata = []
    
    try:
        for file in files:
            if not file.filename:
                continue
                
            # Generate unique filename to avoid conflicts
            import uuid
            file_id = str(uuid.uuid4())
            suffix = os.path.splitext(file.filename)[1]
            saved_filename = f"{file_id}{suffix}"
            saved_path = UPLOADS_DIR / saved_filename
            
            # Save file permanently
            content = await file.read()
            with open(saved_path, "wb") as f:
                f.write(content)
            
            saved_file_paths.append(str(saved_path))
            file_metadata.append({
                "original_filename": file.filename,
                "saved_filename": saved_filename,
                "saved_path": str(saved_path),
                "file_id": file_id
            })

        # Process documents
        document_data = process_documents(saved_file_paths)

        # Extract data from document
        extracted_data = extract_field_from_document(document_data)

        response_data = {
            "extracted_data": extracted_data,
            "document_texts": document_data,
            "file_metadata": file_metadata
        }

        # Calculate accuracy if ground truth is provided
        if ground_truth:
            accuracy_calculator = AccuracyCalculator()
            accuracy_result = accuracy_calculator.calculate_document_accuracy(
                extracted_data, ground_truth
            )
            response_data["accuracy"] = accuracy_result

        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")

@router.post("/documents/save")
async def save_document_data(document_data: Dict[str, Any]):
    """Save document data to the JSON store."""
    required_fields = ["extracted_data", "document_texts"]
    if not all(field in document_data for field in required_fields):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # Include file metadata if available
    file_metadata = document_data.get("file_metadata", [])
    
    # Check if this is an update to an existing document by looking at file IDs
    file_ids = [meta.get("file_id") for meta in file_metadata if meta.get("file_id")]
    existing_doc_id = None
    
    if file_ids:
        existing_doc_id = storage_service.find_document_by_file_ids(file_ids)
    
    if existing_doc_id:
        # Update existing document
        success = storage_service.update_existing_document(
            existing_doc_id,
            document_data["extracted_data"], 
            document_data["document_texts"],
            file_metadata
        )
        if success:
            return {
                "document_id": existing_doc_id,
                "message": "Document updated successfully",
                "action": "updated"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update existing document")
    else:
        # Create new document
        doc_id = storage_service.save_document(
            document_data["extracted_data"], 
            document_data["document_texts"],
            file_metadata
        )
        
        return {
            "document_id": doc_id,
            "message": "Document saved successfully",
            "action": "created"
        }

@router.get("/files/{filename}")
async def serve_file(filename: str, download: bool = False):
    """Serve uploaded files."""
    file_path = UPLOADS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Find original filename by searching through all documents
    original_filename = filename  # fallback to saved filename
    for doc_data in storage_service.data["documents"].values():
        file_metadata = doc_data.get("file_metadata", [])
        for meta in file_metadata:
            if meta.get("saved_filename") == filename:
                original_filename = meta.get("original_filename", filename)
                break
        if original_filename != filename:
            break
    
    # Determine media type based on file extension
    if filename.lower().endswith('.pdf'):
        media_type = 'application/pdf'
    elif filename.lower().endswith(('.xlsx', '.xls')):
        media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        media_type = 'application/octet-stream'
    
    # Set appropriate Content-Disposition header
    if download:
        content_disposition = f'attachment; filename="{original_filename}"'
    else:
        content_disposition = "inline"
    
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=original_filename,
        headers={
            "Content-Disposition": content_disposition
        }
    )

@router.get("/files/{filename}/parsed")
async def serve_parsed_excel(filename: str):
    """Parse Excel file and return as JSON data for rendering."""
    file_path = UPLOADS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if not filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File is not an Excel file")
    
    try:
        from app.utils.xlsx_utils import parse_excel_to_json
        excel_data = parse_excel_to_json(str(file_path))
        return {"sheets": excel_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing Excel file: {str(e)}")

@router.get("/documents/{doc_id}")
async def get_document_data(doc_id: str):
    """Get document data by ID."""
    document_data = storage_service.get_document(doc_id)
    if not document_data:
        raise HTTPException(status_code=404, detail="Document not found")
    return document_data

@router.put("/documents/{doc_id}/field")
async def update_document_field(doc_id: str, field_data: Dict[str, Any]):
    """Update a specific field in the document's extracted data."""
    if "field" not in field_data or "value" not in field_data:
        raise HTTPException(status_code=400, detail="Both 'field' and 'value' are required")
    
    success = storage_service.update_document_field(doc_id, field_data["field"], field_data["value"])
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Field updated successfully"}

@router.get("/documents")
async def list_documents():
    """List all documents."""
    return {"documents": storage_service.list_documents()}

@router.get("/documents/latest")
async def get_latest_document():
    """Get the most recently processed document."""
    document_data = storage_service.get_latest_document()
    if not document_data:
        raise HTTPException(status_code=404, detail="No documents found")
    return document_data

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document."""
    success = storage_service.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document deleted successfully"} 
