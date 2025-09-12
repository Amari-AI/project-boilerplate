from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import tempfile

from app.services.document_processor import process_documents
from app.services.llm_service import extract_field_from_document
from app.models.shipment import ProcessDocumentsResponse

router = APIRouter()

@router.post("/process-documents", response_model=ProcessDocumentsResponse)
async def process_documents_endpoint(
    files: List[UploadFile] = File(...)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Check file types
    allowed_extensions = {'.pdf', '.xlsx', '.xls'}
    for file in files:
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(status_code=400, detail=f"File type not allowed: {file.filename}")
    
    temp_file_paths = []
    try:
        for file in files:
            # Create temp file with proper suffix
            suffix = os.path.splitext(file.filename)[1] if file.filename else ""
            temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            temp_file_paths.append(temp_file.name)

            # Write content to temp file
            content = await file.read()
            temp_file.write(content)
            temp_file.close()

        # Process documents
        document_data = process_documents(temp_file_paths)

        # Extract data from document
        extracted_data = extract_field_from_document(document_data)

        return ProcessDocumentsResponse(
            extracted_data=extracted_data,
            document_texts=document_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")
    finally:
        # Clean up temp files
        for path in temp_file_paths:
            try:
                os.unlink(path)
            except:
                pass 
