from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from openpyxl import load_workbook


def extract_text_from_xlsx(file_path: str) -> str:
    """
    Extracts a readable text dump from an .xlsx workbook.
    Concatenates all non-empty cell values across all sheets.
    """
    try:
        wb = load_workbook(file_path, data_only=True, read_only=True)
    except Exception:
        return ""

    parts: List[str] = []
    for ws in wb.worksheets:
        parts.append(f"Sheet: {ws.title}")
        try:
            for row in ws.iter_rows(values_only=True):
                values = [str(v).strip() for v in row if v is not None and str(v).strip() != ""]
                if values:
                    parts.append(" \t ".join(values))
        except Exception:
            # If any worksheet fails, continue with others
            continue

    return "\n".join(parts).strip()


def parse_line_items_metrics(file_path: str) -> Dict[str, Optional[float]]:
    """
    Tries to infer line item count and averages for gross weight and price
    from typical invoice/packing-list worksheets.

    Heuristic approach:
    - Find a header row containing common header names (e.g., Description, Quantity, Price, Gross Weight)
    - For subsequent rows with content in the description column, attempt to parse numeric values
      for weight and price columns
    - Compute count and averages
    """
    try:
        wb = load_workbook(file_path, data_only=True)
    except Exception:
        return {
            "line_items_count": None,
            "average_gross_weight": None,
            "average_price": None,
        }

    header_aliases = {
        "description": {"description", "item", "product", "goods"},
        "quantity": {"qty", "quantity"},
        "price": {"price", "unit price", "amount", "value", "unit_value"},
        "gross_weight": {"gross weight", "weight", "g.w.", "g/w", "gw"},
    }

    def normalize(s: str) -> str:
        return " ".join(s.strip().lower().split())

    best_metrics = {
        "line_items_count": None,
        "average_gross_weight": None,
        "average_price": None,
    }

    for ws in wb.worksheets:
        header_row_idx = None
        col_map: Dict[str, int] = {}

        # Find header row
        for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
            labels = [normalize(str(v)) for v in row if v is not None]
            if not labels:
                continue
            # Try to map columns by header names
            for j, v in enumerate(row):
                if v is None:
                    continue
                cell = normalize(str(v))
                for key, aliases in header_aliases.items():
                    if cell in aliases and key not in col_map:
                        col_map[key] = j
            # Consider it a header if we matched at least a description and one numeric column
            if "description" in col_map and ("price" in col_map or "gross_weight" in col_map):
                header_row_idx = i
                break

        if header_row_idx is None:
            continue

        # Parse subsequent rows
        item_count = 0
        weights: List[float] = []
        prices: List[float] = []

        for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
            if i <= header_row_idx:
                continue
            values = list(row)
            # Stop if we hit a fully empty row
            if all(v is None or str(v).strip() == "" for v in values):
                # continue scanning; invoices sometimes have empty lines
                continue

            # Item presence indicated by description text
            desc = values[col_map["description"]] if "description" in col_map and col_map["description"] < len(values) else None
            if desc is None or str(desc).strip() == "":
                continue
            item_count += 1

            # Collect numeric metrics when present
            if "gross_weight" in col_map and col_map["gross_weight"] < len(values):
                w = _as_float(values[col_map["gross_weight"]])
                if w is not None:
                    weights.append(w)
            if "price" in col_map and col_map["price"] < len(values):
                p = _as_float(values[col_map["price"]])
                if p is not None:
                    prices.append(p)

        # Update best metrics if better coverage found
        if item_count > 0:
            best_metrics["line_items_count"] = item_count
            best_metrics["average_gross_weight"] = (
                sum(weights) / len(weights) if weights else None
            )
            best_metrics["average_price"] = (
                sum(prices) / len(prices) if prices else None
            )

            # Prefer the first worksheet that yields items
            break

    return best_metrics


def _as_float(val) -> Optional[float]:
    try:
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val).strip().replace(",", "")
        # Strip currency symbols
        if s and s[0] in "$€£₹":
            s = s[1:]
        return float(s)
    except Exception:
        return None

