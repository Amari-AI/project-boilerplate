import pytest
from pathlib import Path

from app.services.document_processor import process_documents


def test_process_documents_aggregates_pdf_xlsx(monkeypatch, tmp_path):
    # Create dummy files with the right extensions
    pdf_file = tmp_path / "sample.pdf"
    xlsx_file = tmp_path / "sample.xlsx"
    pdf_file.write_bytes(b"%PDF-1.4 dummy content")
    xlsx_file.write_bytes(b"PK\x03\x04 dummy content")

    # Mock text extraction
    monkeypatch.setattr(
        "app.services.document_processor.extract_text_from_pdf",
        lambda p: "EXTRACTED_PDF_TEXT",
    )
    monkeypatch.setattr(
        "app.services.document_processor.extract_text_from_xlsx",
        lambda p: "EXTRACTED_XLSX_TEXT",
    )
    # Mock metrics parsing
    monkeypatch.setattr(
        "app.services.document_processor.parse_line_items_metrics",
        lambda p: {"line_items_count": 2, "average_gross_weight": 10.0, "average_price": 5.0},
    )

    result = process_documents([str(pdf_file), str(xlsx_file)])

    assert isinstance(result, dict)
    assert result["pdf_texts"] == ["EXTRACTED_PDF_TEXT"]
    assert result["xlsx_texts"] == ["EXTRACTED_XLSX_TEXT"]
    assert "EXTRACTED_PDF_TEXT" in result["raw_text"]
    assert "EXTRACTED_XLSX_TEXT" in result["raw_text"]
    assert result["metrics"] == {"line_items_count": 2, "average_gross_weight": 10.0, "average_price": 5.0}


def test_process_documents_multiple_pdfs_collects_all(monkeypatch, tmp_path):
    # Two PDFs should yield both texts in order
    pdf1 = tmp_path / "a.pdf"
    pdf2 = tmp_path / "b.pdf"
    pdf1.write_bytes(b"%PDF-1.4 A")
    pdf2.write_bytes(b"%PDF-1.4 B")

    texts = {str(pdf1): "TEXT_A", str(pdf2): "TEXT_B"}

    def fake_extract(path):
        return texts[str(path)]

    monkeypatch.setattr("app.services.document_processor.extract_text_from_pdf", fake_extract)

    result = process_documents([str(pdf1), str(pdf2)])

    assert result["pdf_texts"] == ["TEXT_A", "TEXT_B"]
    assert result["raw_text"].startswith("TEXT_A")
    assert "TEXT_B" in result["raw_text"]


def test_process_documents_skips_unsupported(monkeypatch, tmp_path):
    other = tmp_path / "note.txt"
    other.write_text("hello")

    # If only unsupported files are passed, raw_text should be empty
    result = process_documents([str(other)])
    assert result["pdf_texts"] == []
    assert result["xlsx_texts"] == []
    assert result["raw_text"] == ""
