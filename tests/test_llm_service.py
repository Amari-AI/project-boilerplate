from app.services.llm_service import extract_field_from_document


def test_extract_field_from_document_rule_based_and_xlsx_metrics():
    # Craft raw text that matches rule-based patterns
    raw_text = (
        "Bill of Lading No: ABC12345\n"
        "Container: MSKU1234567\n"
        "Consignee: John Doe\n123 Main St, Springfield\n"
        "Date: 2024-09-05\n"
    )
    metrics = {"line_items_count": 3, "average_gross_weight": 50.0, "average_price": 100.0}
    document_data = {"raw_text": raw_text, "metrics": metrics}

    result = extract_field_from_document(document_data)

    # Top-level fields from rules
    assert result["bill_of_lading_number"] == "ABC12345"
    assert result["container_number"] == "MSKU1234567"
    assert result["consignee_name"] == "John Doe"
    assert "123 Main St" in (result["consignee_address"] or "")
    assert result["date"] == "2024-09-05"

    # Items absent; metrics filled from xlsx
    assert result.get("items") == []
    assert result["line_items_count"] == 3
    assert result["average_gross_weight"] == 50.0
    assert result["average_price"] == 100.0

    # Provenance expectations
    prov = result.get("provenance") or {}
    assert prov.get("bill_of_lading_number") == "rule"
    assert prov.get("container_number") == "rule"
    assert prov.get("consignee_name") == "rule"
    assert prov.get("consignee_address") == "rule"
    assert prov.get("date") == "rule"
    assert prov.get("line_items_count") == "xlsx"
    assert prov.get("average_gross_weight") == "xlsx"
    assert prov.get("average_price") == "xlsx"

    # No LLM used in this scenario (no API key)
    assert result.get("llm_provider") is None

