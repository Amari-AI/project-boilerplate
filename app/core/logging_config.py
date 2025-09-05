import logging
import os
from app.core.config import settings


def setup_logging() -> None:
    level_name = (settings.LOG_LEVEL or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # Basic configuration for root logger if not already configured
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
    else:
        logging.getLogger().setLevel(level)

    # Align common servers' loggers
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        try:
            logging.getLogger(name).setLevel(level)
        except Exception:
            pass

