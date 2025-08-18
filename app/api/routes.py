from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import tempfile

from app.core.config import settings
from app.core.models import ExtractedData
from app.services.document_processor import process_documents
from app.services.llm_service import extract_all_fields_from_documents

router = APIRouter()


@router.post("/process-documents", response_model=ExtractedData)
async def process_documents_endpoint(files: List[UploadFile] = File(...)):
    """
    Process uploaded documents and extract structured data.

    Args:
        files: List of uploaded files (PDF, Excel)

    Returns:
        ExtractedData: Structured data extracted from the documents
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    temp_file_paths = []

    try:
        # Save uploaded files to temporary locations
        for file in files:
            if not file.filename:
                continue

            # Validate file type
            if not (
                file.filename.lower().endswith(tuple(settings.ALLOWED_DOCUMENT_TYPES))
            ):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.filename}. Only {', '.join(settings.ALLOWED_DOCUMENT_TYPES)} files are supported.",
                )

            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                suffix=os.path.splitext(file.filename)[1], delete=False
            )
            temp_file_paths.append(temp_file.name)

            # Write file content
            content = await file.read()
            temp_file.write(content)
            temp_file.close()

        if not temp_file_paths:
            raise HTTPException(status_code=400, detail="No valid files to process")

        # Process documents to extract text
        document_data = process_documents(temp_file_paths)

        # Convert document data to list of text strings
        document_texts = []
        if "pdf_text" in document_data and document_data["pdf_text"]:
            document_texts.append(document_data["pdf_text"])
        if "excel_text" in document_data and document_data["excel_text"]:
            document_texts.append(document_data["excel_text"])

        if not document_texts:
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the uploaded documents",
            )

        # Extract structured data using LLM
        extracted_data = await extract_all_fields_from_documents(document_texts)
        # print(f"DEBUG API: Extracted data: {extracted_data}")

        # Clean up temporary files after processing
        for temp_path in temp_file_paths:
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except OSError as e:
                # Log error but don't fail the request
                print(f"Warning: Could not delete temporary file {temp_path}: {e}")

        return extracted_data

    except HTTPException:
        # Clean up temporary files on HTTP exception
        for temp_path in temp_file_paths:
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except OSError:
                pass
        raise
    except Exception as e:
        # Clean up temporary files on general exception
        for temp_path in temp_file_paths:
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except OSError:
                pass
        raise HTTPException(
            status_code=500, detail=f"Error processing documents: {str(e)}"
        )
