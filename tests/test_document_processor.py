import pytest
from app.services.document_processor import process_documents
from pathlib import Path

# TODO: Incomplete tests
def test_process_documents():
    # Test with sample files
    sample_files = [
        # str(Path("documents/sample_bill_of_lading.pdf")),
        str(Path("documents/InvoicePackingList.xlsx"))
    ]
    result = process_documents(sample_files)
    
    # Missing assertions
