from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import tempfile

from app.services.document_processor import process_documents
from app.services.llm_service import extract_field_from_document

router = APIRouter()

@router.post("/process-documents", response_model=dict)
async def process_documents_endpoint(
    files: List[UploadFile] = File(...)
):
    temp_file_paths = []
    file_names = []
    
    for file in files:
        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(suffix=file.filename, delete=False)
        temp_file_paths.append(temp_file.name)
        file_names.append(file.filename)

        # Write content to temp file
        content = await file.read()
        temp_file.write(content)
        temp_file.close()

    # Process each file individually to track data sources
    file_results = []
    combined_text = ""
    combined_images = []
    
    for i, file_path in enumerate(temp_file_paths):
        # Process single document
        document_data = process_documents([file_path])
        
        # Extract data from this specific document
        file_extracted_data = extract_field_from_document(
            document_text=document_data.get('text', ''),
            images=document_data.get('images', [])
        )
        
        # Store results with file source information
        file_result = {
            "file_name": file_names[i],
            "file_info": document_data['file_info'][0] if document_data['file_info'] else {},
            "extracted_data": file_extracted_data
        }
        file_results.append(file_result)
        
        # Also combine data for overall extraction
        if document_data.get('text'):
            combined_text += document_data['text']
        if document_data.get('images'):
            combined_images.extend(document_data['images'])

    # Clean up temp files
    for path in temp_file_paths:
        os.unlink(path)

    return {
        "file_results": file_results,  # Individual file results
        "processing_info": {
            "files_processed": len(files),
            "images_processed": len(combined_images)
        }
    } 
