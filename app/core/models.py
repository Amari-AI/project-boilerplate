from pydantic import BaseModel
from typing import Optional, get_origin, get_args, Union
from datetime import datetime


class ExtractedData(BaseModel):
    bill_of_lading_number: Optional[str] = None
    container_number: Optional[str] = None
    consignee_name: Optional[str] = None
    consignee: Optional[str] = None
    date: Optional[datetime] = None
    line_items_count: Optional[int] = None
    average_gross_weight: Optional[float] = None
    average_price: Optional[float] = None

    def format_for_llm(self) -> str:
        """
        Create a string representation of the data fields for LLM processing.

        Returns:
            str: Formatted string with field names and descriptions
        """
        fields = [
            "bill_of_lading_number: Bill of Lading Number",
            "container_number: Container Number",
            "consignee_name: Consignee Name",
            "consignee: Consignee",
            "date: Date",
            "line_items_count: Line Items Count",
            "average_gross_weight: Average Gross Weight",
            "average_price: Average Price",
        ]
        return "\n".join(fields)

    @classmethod
    def get_field_names(cls) -> list[str]:
        """
        Get list of field names for LLM processing.

        Returns:
            list[str]: List of field names
        """
        return [
            "bill_of_lading_number",
            "container_number",
            "consignee_name",
            "consignee",
            "date",
            "line_items_count",
            "average_gross_weight",
            "average_price",
        ]

    @classmethod
    def get_field_info(cls) -> dict[str, str]:
        """
        Get field names and their corresponding data types for LLM processing.

        Returns:
            dict[str, str]: Dictionary mapping field names to data type strings
        """
        field_info = {}

        for field_name, field_info_obj in cls.model_fields.items():
            field_type = field_info_obj.annotation

            # Handle Optional[Type] -> Type (Optional[X] is Union[X, None])
            if get_origin(field_type) is Union:
                args = get_args(field_type)
                # Optional[X] becomes Union[X, NoneType]
                inner_type = (
                    args[0] if len(args) == 2 and type(None) in args else field_type
                )
            else:
                inner_type = field_type

            # Map Python types to string representations
            if inner_type is str:
                data_type = "string"
            elif inner_type is int:
                data_type = "integer"
            elif inner_type is float:
                data_type = "number"
            elif inner_type is datetime:
                data_type = "datetime"
            elif inner_type is bool:
                data_type = "boolean"
            else:
                data_type = "string"

            field_info[field_name] = data_type

        return field_info
