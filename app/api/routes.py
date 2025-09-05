from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import tempfile

from app.services.document_processor import process_documents
from app.services.llm_service import extract_field_from_document, extract_field_from_pdf_files

router = APIRouter()

@router.post("/process-documents", response_model=dict)
async def process_documents_endpoint(
    files: List[UploadFile] = File(...)
):
    temp_file_paths = []
    for file in files:
        # Save uploaded file temporarily (in binary mode for PDFs)
        temp_file = tempfile.NamedTemporaryFile(suffix=file.filename, delete=False, mode='wb')
        temp_file_paths.append(temp_file.name)

        # Write binary content to temp file
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        
        print(f"DEBUG API: Saved {file.filename} to {temp_file.name}, size: {len(content)} bytes")

    # Check if we have PDF files to process directly with Claude
    pdf_files = [path for path in temp_file_paths if path.lower().endswith('.pdf')]
    
    if pdf_files:
        # Use Claude's native PDF processing for PDF files
        result = extract_field_from_pdf_files(pdf_files)
    else:
        # Fallback to text-based processing for other files
        document_data = process_documents(temp_file_paths)
        result = extract_field_from_document(document_data)

    # Clean up temp files
    for path in temp_file_paths:
        os.unlink(path)

    return result 
