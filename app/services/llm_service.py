import json
import logging
import re
from typing import Dict, Optional, Tuple, List
from app.core.config import settings
from app.models.extraction import DocumentExtraction, LineItem

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - library optional at runtime
    OpenAI = None

try:
    from anthropic import Anthropic
except Exception:  # pragma: no cover - library optional at runtime
    Anthropic = None


def extract_field_from_document(document_data: Dict) -> Dict:
    """
    Primary LLM-based extraction returning structured items array; aggregates are computed locally.
    Falls back to rule-based patterns for missing fields, and to XLSX metrics if items are absent.
    """
    text = (document_data or {}).get("raw_text", "")

    # Start with empty result and provenance
    result: Dict = {
        "bill_of_lading_number": None,
        "container_number": None,
        "consignee_name": None,
        "consignee_address": None,
        "date": None,
        "line_items_count": None,
        "average_gross_weight": None,
        "average_price": None,
        "raw_text": text,
    }
    provenance = {k: "none" for k in (
        "bill_of_lading_number",
        "container_number",
        "consignee_name",
        "consignee_address",
        "date",
        "line_items_count",
        "average_gross_weight",
        "average_price",
    )}

    provider_used: Optional[str] = None
    items: List[LineItem] = []

    # Try LLM structured extraction first
    if not settings.LLM_FALLBACK_ENABLED:
        logger.info("LLM insights skipped: disabled by LLM_FALLBACK_ENABLED=false")
    elif not _llm_available():
        logger.info("LLM insights skipped: %s", _llm_availability_reason())
    else:
        logger.info("Attempting primary LLM structured extraction")
        llm_data, provider = extract_with_llm_structured(text)
        if llm_data:
            provider_used = provider
            try:
                doc = DocumentExtraction.model_validate(llm_data)
                # Top-level fields
                for k in ("bill_of_lading_number", "container_number", "consignee_name", "consignee_address", "date"):
                    val = getattr(doc, k)
                    if val not in (None, ""):
                        result[k] = val
                        provenance[k] = provider or "llm"
                items = doc.items or []
            except Exception as e:
                logger.warning("LLM JSON did not match schema: %s", e)
        else:
            logger.info("LLM returned empty/invalid payload; will use fallbacks")

    # If items present from LLM, attach to result and compute aggregates manually
    if items:
        # expose the items for auditing in API response
        result["items"] = [i.model_dump() for i in items]
        count, avg_w, avg_p = _compute_aggregates(items)
        result["line_items_count"] = count
        result["average_gross_weight"] = avg_w
        result["average_price"] = avg_p
        for k in ("line_items_count", "average_gross_weight", "average_price"):
            provenance[k] = "manual"
    else:
        result["items"] = []
        # Fall back to spreadsheet-derived metrics if available
        met = (document_data or {}).get("metrics", {})
        for k in ("line_items_count", "average_gross_weight", "average_price"):
            if met.get(k) is not None:
                result[k] = met.get(k)
                provenance[k] = "xlsx"

    # Fill any missing top-level fields using rule-based heuristics as last resort
    if not result.get("bill_of_lading_number"):
        result["bill_of_lading_number"] = _find_bill_of_lading(text)
        if result["bill_of_lading_number"]:
            provenance["bill_of_lading_number"] = "rule"
    if not result.get("container_number"):
        result["container_number"] = _find_container_number(text)
        if result["container_number"]:
            provenance["container_number"] = "rule"
    if not result.get("date"):
        result["date"] = _find_date(text)
        if result["date"]:
            provenance["date"] = "rule"
    if not result.get("consignee_name") or not result.get("consignee_address"):
        consignee = _find_consignee_block(text)
        if consignee:
            if not result.get("consignee_name"):
                result["consignee_name"] = consignee.get("name")
                provenance["consignee_name"] = "rule"
            if not result.get("consignee_address"):
                result["consignee_address"] = consignee.get("address")
                provenance["consignee_address"] = "rule"

    result["provenance"] = provenance
    result["llm_provider"] = provider_used
    return result


def _find_bill_of_lading(text: str) -> Optional[str]:
    patterns = [
        r"\b(?:bill\s*of\s*lading|b/?l|bol)\s*(?:no\.?|number|#)?\s*[:\-]?\s*([A-Za-z0-9\-]+)",
        r"\bBOL[:\s#-]*([A-Za-z0-9\-]+)",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def _find_container_number(text: str) -> Optional[str]:
    # ISO 6346: 4 letters + 7 digits, sometimes separated by spaces or punctuation
    m = re.search(r"\b([A-Z]{4}\s?\d{7})\b", text)
    if m:
        return m.group(1).replace(" ", "").strip()
    return None


def _find_consignee_block(text: str) -> Optional[Dict[str, str]]:
    # Capture a few lines following a 'Consignee' label
    # Allow lines separated by newlines; stop at a blank line or another header-like keyword
    block_pat = re.compile(
        r"consignee\s*[:\-]?\s*(.+?)(?:\n\s*\n|\n\s*(shipper|notify|buyer|supplier)\b|$)",
        re.IGNORECASE | re.DOTALL,
    )
    m = block_pat.search(text)
    if not m:
        return None
    block = m.group(1).strip()
    # Assume first line is name, rest is address
    lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
    if not lines:
        return None
    name = lines[0]
    address = "; ".join(lines[1:]) if len(lines) > 1 else None
    return {"name": name, "address": address}


def _find_date(text: str) -> Optional[str]:
    # Try several common formats, return the first match as-is
    date_patterns = [
        r"\b(\d{4}-\d{2}-\d{2})\b",  # 2024-09-05
        r"\b(\d{2}/\d{2}/\d{4})\b",  # 09/05/2024 or 05/09/2024
        r"\b(\d{2}-\d{2}-\d{4})\b",  # 09-05-2024
        r"\b([A-Za-z]{3,9}\s+\d{1,2},\s*\d{4})\b",  # September 5, 2024
    ]
    for pat in date_patterns:
        m = re.search(pat, text)
        if m:
            return m.group(1)
    return None


def _should_use_llm_fallback(res: Dict) -> bool:
    # Deprecated in the new flow; kept for compatibility if needed elsewhere
    if not settings.LLM_FALLBACK_ENABLED:
        return False
    critical = ["bill_of_lading_number", "container_number", "consignee_name", "consignee_address", "date"]
    return any(not res.get(k) for k in critical)


def _llm_available() -> bool:
    # Either OpenAI or Anthropic is acceptable
    if settings.OPENAI_API_KEY and OpenAI is not None:
        return True
    if settings.ANTHROPIC_API_KEY and Anthropic is not None:
        return True
    return False


def extract_with_llm(text: str) -> Tuple[Dict, Optional[str]]:
    """
    Use OpenAI Chat Completions to extract fields as JSON. Returns a dict.
    Never raises; returns empty dict on failure.
    """
    # Legacy method retained; now superseded by extract_with_llm_structured
    schema_keys = ["bill_of_lading_number", "container_number", "consignee_name", "consignee_address", "date"]
    system = ("You extract shipment fields from raw OCR/text. Return a compact JSON with keys: " + ", ".join(schema_keys) + ". Use null when not found.")
    user = ("Extract fields from this document text. Keep units out of numeric fields.\n\n" + text)
    # Prefer OpenAI if configured, else try Anthropic
    if settings.OPENAI_API_KEY and OpenAI is not None:
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )
            content = resp.choices[0].message.content
            data = json.loads(content)
            if isinstance(data, dict):
                logger.info("OpenAI extraction succeeded")
                return data, "openai"
        except Exception as e:
            logger.warning("OpenAI extraction failed: %s", e)

    if settings.ANTHROPIC_API_KEY and Anthropic is not None:
        try:
            client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            resp = client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=800,
                temperature=0,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            # Anthropic returns a content list; join text blocks
            parts = []
            for block in getattr(resp, "content", []) or []:
                txt = getattr(block, "text", None)
                if txt:
                    parts.append(txt)
            content = "\n".join(parts)
            data = json.loads(content)
            if isinstance(data, dict):
                logger.info("Anthropic extraction succeeded")
                return data, "anthropic"
        except Exception as e:
            logger.warning("Anthropic extraction failed: %s", e)

    return {}, None


def _llm_availability_reason() -> str:
    if not settings.LLM_FALLBACK_ENABLED:
        return "disabled by config"
    if settings.OPENAI_API_KEY:
        if OpenAI is None:
            return "OpenAI SDK not installed"
        return "OpenAI available"
    if settings.ANTHROPIC_API_KEY:
        if Anthropic is None:
            return "Anthropic SDK not installed"
        return "Anthropic available"
    return "no LLM API key configured"


def extract_with_llm_structured(text: str) -> Tuple[Dict, Optional[str]]:
    """
    Ask the LLM for a strict JSON with an items array for manual aggregation.
    JSON schema:
    {
      "bill_of_lading_number": str|null,
      "container_number": str|null,
      "consignee_name": str|null,
      "consignee_address": str|null,
      "date": str|null,
      "items": [
        {"description": str|null, "quantity": number|null, "gross_weight": number|null, "unit_price": number|null}
      ]
    }
    """
    system = (
        "You extract structured shipment data from raw OCR/text. "
        "Return only a compact JSON object with exactly these keys: "
        "bill_of_lading_number, container_number, consignee_name, consignee_address, date, items. "
        "In items, each object should contain: description, quantity, gross_weight, unit_price. "
        "Use numbers (not strings) for numeric fields when possible, and null when not found."
    )
    user = "Extract the fields and items from this document text. Keep units out of numeric fields.\n\n" + text

    # Prefer OpenAI if configured
    if settings.OPENAI_API_KEY and OpenAI is not None:
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )
            content = resp.choices[0].message.content
            data = json.loads(content)
            if isinstance(data, dict):
                logger.info("OpenAI structured extraction succeeded")
                return data, "openai"
        except Exception as e:
            logger.warning("OpenAI structured extraction failed: %s", e)

    # Try Anthropic
    if settings.ANTHROPIC_API_KEY and Anthropic is not None:
        try:
            client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            resp = client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=1200,
                temperature=0,
                system=system + " Return only JSON with no commentary.",
                messages=[{"role": "user", "content": user}],
            )
            parts = []
            for block in getattr(resp, "content", []) or []:
                txt = getattr(block, "text", None)
                if txt:
                    parts.append(txt)
            content = "\n".join(parts)
            data = json.loads(content)
            if isinstance(data, dict):
                logger.info("Anthropic structured extraction succeeded")
                return data, "anthropic"
        except Exception as e:
            logger.warning("Anthropic structured extraction failed: %s", e)

    return {}, None


def _compute_aggregates(items: List[LineItem]) -> Tuple[int, Optional[float], Optional[float]]:
    count = len(items)
    weights = [i.gross_weight for i in items if getattr(i, "gross_weight", None) is not None]
    prices = [i.unit_price for i in items if getattr(i, "unit_price", None) is not None]
    avg_w = sum(weights) / len(weights) if weights else None
    avg_p = sum(prices) / len(prices) if prices else None
    return count, avg_w, avg_p


def _merge_missing(base: Dict, extra: Dict) -> Dict:
    if not extra:
        return base
    merged = dict(base)
    for k, v in extra.items():
        if merged.get(k) in (None, "") and v not in (None, ""):
            merged[k] = v
    return merged
