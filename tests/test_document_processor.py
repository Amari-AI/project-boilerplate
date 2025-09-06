import pytest
from pathlib import Path

from app.services.document_processor import process_documents


def test_process_documents_handles_pdf_only(monkeypatch, tmp_path):
    # Create dummy files with the right extensions
    pdf_file = tmp_path / "sample.pdf"
    xlsx_file = tmp_path / "sample.xlsx"
    pdf_file.write_bytes(b"%PDF-1.4 dummy content")
    xlsx_file.write_bytes(b"PK\x03\x04 dummy content")

    # Mock the PDF text extraction to avoid relying on PyPDF2 internals
    monkeypatch.setattr(
        "app.services.document_processor.extract_text_from_pdf",
        lambda p: "EXTRACTED_PDF_TEXT",
    )

    result = process_documents([str(pdf_file), str(xlsx_file)])

    assert isinstance(result, dict)
    assert result.get("pdf_text") == "EXTRACTED_PDF_TEXT"


def test_process_documents_multiple_pdfs_overwrites(monkeypatch, tmp_path):
    # Two PDFs to verify last write wins in current implementation
    pdf1 = tmp_path / "a.pdf"
    pdf2 = tmp_path / "b.pdf"
    pdf1.write_bytes(b"%PDF-1.4 A")
    pdf2.write_bytes(b"%PDF-1.4 B")

    texts = {str(pdf1): "TEXT_A", str(pdf2): "TEXT_B"}

    def fake_extract(path):
        return texts[str(path)]

    monkeypatch.setattr("app.services.document_processor.extract_text_from_pdf", fake_extract)

    result = process_documents([str(pdf1), str(pdf2)])

    # Current behavior overwrites the key for each PDF; assert last one remains
    assert result == {"pdf_text": "TEXT_B"}
