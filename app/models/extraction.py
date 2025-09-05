from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    gross_weight: Optional[float] = None
    unit_price: Optional[float] = None


class DocumentExtraction(BaseModel):
    bill_of_lading_number: Optional[str] = None
    container_number: Optional[str] = None
    consignee_name: Optional[str] = None
    consignee_address: Optional[str] = None
    date: Optional[str] = None
    items: List[LineItem] = Field(default_factory=list)

