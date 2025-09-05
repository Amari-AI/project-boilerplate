import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import tempfile

from app.services.document_processor import process_documents
from app.services.llm_service import extract_field_from_document

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/process-documents", response_model=dict)
async def process_documents_endpoint(
    files: List[UploadFile] = File(...)
):
    temp_file_paths = []
    logger.info("Received %d files for processing", len(files))
    for file in files:
        # Save uploaded file temporarily
        _, ext = os.path.splitext(file.filename)
        temp_file = tempfile.NamedTemporaryFile(suffix=ext or "", delete=False)
        temp_file_paths.append(temp_file.name)

        # Write content to temp file
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        logger.info("Saved upload '%s' (%d bytes) to '%s'", file.filename, len(content), temp_file.name)

    # Process documents
    try:
        logger.info("Starting document processing for %d files", len(temp_file_paths))
        document_data = process_documents(temp_file_paths)
        logger.info("Document processing completed: keys=%s", list(document_data.keys()))
    except Exception as e:
        # Clean up temp files before raising
        for path in temp_file_paths:
            try:
                os.unlink(path)
            except Exception:
                pass
        logger.exception("Failed to process documents: %s", e)
        raise HTTPException(status_code=400, detail=f"Failed to process documents: {e}")

    # Extract data from document
    extracted_data = extract_field_from_document(document_data)
    logger.info(
        "Extraction complete. Provider=%s, Items=%s, Provenance=%s",
        extracted_data.get("llm_provider"),
        len(extracted_data.get("items") or []),
        extracted_data.get("provenance"),
    )

    # Clean up temp files
    for path in temp_file_paths:
        try:
            os.unlink(path)
            logger.info("Cleaned up temp file '%s'", path)
        except Exception as cleanup_err:
            logger.warning("Failed to delete temp file '%s': %s", path, cleanup_err)

    return {"extracted_data": extracted_data}
