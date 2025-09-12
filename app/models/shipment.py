from pydantic import BaseModel
from typing import Optional
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

class ProcessDocumentsResponse(BaseModel):
    """Response model for document processing"""
    extracted_data: ShipmentData
    document_texts: dict = {}