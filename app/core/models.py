from pydantic import BaseModel, Field


class InvoiceItem(BaseModel):
    """
    Invoice item model.
    """

    serial_number: str = Field(description="Serial number of the item")
    description: str = Field(description="Description of the item")
    quantity: int = Field(description="Quantity of the item")
    unit_value: float = Field(description="Unit value of the item")
    total_weight: float = Field(description="Total weight of the item")
    other_identifier: str | None = Field(
        default=None, description="Any other identifier of the item"
    )


class Invoice(BaseModel):
    """
    Invoice model.
    """

    invoice_number: str = Field(description="Invoice number")
    invoice_items: list[InvoiceItem] = Field(description="List of invoice items")


class BillOfLading(BaseModel):
    """
    Bill of lading model.
    """

    bill_of_landing_number: str = Field(description="Bill of landing number")
    container_number: str = Field(description="Container number")
    consignee_name: str = Field(description="Consignee name")
    consignee_address: str = Field(description="Consignee address")
    date: str = Field(description="Export date")


class ExtractedData(BaseModel):
    """
    Extracted data model.
    """

    invoice_list: Invoice | None = Field(default=None, description="List of invoices")
    bill_of_lading_list: BillOfLading | None = Field(
        default=None, description="List of bill of ladings"
    )
