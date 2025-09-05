from __future__ import annotations

import logging
import os
from typing import Dict, List

from app.utils.pdf_utils import extract_text_from_pdf, ocr_text_from_pdf
from app.utils.xlsx_utils import extract_text_from_xlsx, parse_line_items_metrics
from app.core.config import settings

logger = logging.getLogger(__name__)


def process_documents(file_paths: List[str]) -> Dict:
    """
    Process different types of documents and extract raw text and basic metrics.

    Args:
        file_paths: List of paths to the documents

    Returns:
        dict: {
           'pdf_texts': [...],
           'xlsx_texts': [...],
           'raw_text': str,
           'metrics': {
               'line_items_count': Optional[int],
               'average_gross_weight': Optional[float],
               'average_price': Optional[float],
           }
        }
    """
    pdf_texts: List[str] = []
    xlsx_texts: List[str] = []
    metrics_aggregate = {
        "line_items_count": None,
        "average_gross_weight": None,
        "average_price": None,
    }

    allowed = set(settings.ALLOWED_DOCUMENT_TYPES)

    for file_path in file_paths:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in allowed:
            # Skip unsupported files
            logger.warning("Skipping unsupported file '%s'", file_path)
            continue
        if ext == ".pdf":
            logger.info("Extracting PDF text from '%s'", file_path)
            text = extract_text_from_pdf(file_path)
            if len(text) < settings.OCR_MIN_TEXT_CHARS:
                logger.warning(
                    "Primary PDF extraction yielded too little text (%d chars). Trying OCR...",
                    len(text),
                )
                ocr_text = ocr_text_from_pdf(file_path)
                if len(ocr_text) > len(text):
                    logger.info("OCR extraction improved text length to %d chars", len(ocr_text))
                    text = ocr_text
                else:
                    logger.info("OCR did not improve extraction; keeping primary text")
            pdf_texts.append(text)
        elif ext == ".xlsx":
            logger.info("Extracting XLSX text from '%s'", file_path)
            xlsx_texts.append(extract_text_from_xlsx(file_path))
            # Try to parse line item metrics from spreadsheets
            met = parse_line_items_metrics(file_path)
            # Prefer first spreadsheet that yields a line_items_count
            if met.get("line_items_count"):
                metrics_aggregate.update(met)
                logger.info(
                    "Parsed line item metrics from '%s': count=%s, avg_wt=%s, avg_price=%s",
                    file_path,
                    met.get("line_items_count"),
                    met.get("average_gross_weight"),
                    met.get("average_price"),
                )

    raw_text = "\n\n".join([*pdf_texts, *xlsx_texts]).strip()

    return {
        "pdf_texts": pdf_texts,
        "xlsx_texts": xlsx_texts,
        "raw_text": raw_text,
        "metrics": metrics_aggregate,
    }
