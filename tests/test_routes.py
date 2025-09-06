import io

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_root_endpoint():
    client = TestClient(app)
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "Welcome to the Document Processing API"}


def test_process_documents_endpoint_with_uploads(monkeypatch):
    client = TestClient(app)

    # Mock the downstream services to avoid filesystem and network dependencies
    monkeypatch.setattr(
        "app.api.routes.process_documents",
        lambda paths: {"pdf_text": "DUMMY_TEXT"},
    )
    monkeypatch.setattr(
        "app.api.routes.extract_field_from_document",
        lambda document_data: {"summary": "EXTRACTED"},
    )

    files = [
        (
            "files",
            (
                "sample.pdf",
                io.BytesIO(b"%PDF-1.4 sample content"),
                "application/pdf",
            ),
        ),
        (
            "files",
            (
                "sample.xlsx",
                io.BytesIO(b"PK\x03\x04 excel content"),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
        ),
    ]

    res = client.post("/process-documents", files=files)
    assert res.status_code == 200

    body = res.json()
    assert "extracted_data" in body
    assert body["extracted_data"] == {"summary": "EXTRACTED"}

