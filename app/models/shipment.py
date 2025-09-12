from pydantic import BaseModel, field_validator
from typing import Optional, Union
from datetime import date

class ShipmentData(BaseModel):
    """Data model for extracted shipment information"""
    bill_of_lading_number: Optional[str] = None
    container_number: Optional[str] = None
    consignee_name: Optional[str] = None
    consignee_address: Optional[str] = None
    date: Optional[str] = None  # MM/DD/YYYY format
    line_items_count: Optional[str] = None
    average_gross_weight: Optional[str] = None
    average_price: Optional[str] = None

    @field_validator('line_items_count', 'average_gross_weight', 'average_price', mode='before')
    @classmethod
    def convert_to_string(cls, v) -> Optional[str]:
        """Convert numeric values to strings"""
        if v is None:
            return None
        return str(v)

class ProcessDocumentsResponse(BaseModel):
    """Response model for document processing"""
    extracted_data: ShipmentData
    document_texts: dict = {}