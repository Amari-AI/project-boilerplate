import openpyxl
from typing import Dict, Any


def extract_text_from_excel(file_path: str) -> str:
    """
    Extract text from an Excel file and format it for LLM processing.

    Args:
        file_path: Path to the Excel file

    Returns:
        str: Formatted text from all sheets in the Excel file
    """
    try:
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        all_text = []

        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]
            sheet_text = f"Sheet: {sheet_name}\n"
            sheet_text += "=" * (len(sheet_name) + 7) + "\n\n"

            # Get all rows with data
            rows_with_data = []
            for row in worksheet.iter_rows(values_only=True):
                if any(cell is not None and str(cell).strip() for cell in row):
                    rows_with_data.append(row)

            if not rows_with_data:
                sheet_text += "No data found in this sheet.\n\n"
                all_text.append(sheet_text)
                continue

            # Format as table with headers
            headers = rows_with_data[0] if rows_with_data else []
            data_rows = rows_with_data[1:] if len(rows_with_data) > 1 else []

            # Clean and format headers
            cleaned_headers = []
            for header in headers:
                if header is not None:
                    cleaned_headers.append(str(header).strip())
                else:
                    cleaned_headers.append("")

            # Add headers
            if cleaned_headers and any(h for h in cleaned_headers):
                sheet_text += " | ".join(cleaned_headers) + "\n"
                sheet_text += " | ".join(["-" * len(h) for h in cleaned_headers]) + "\n"

            # Add data rows
            for row in data_rows:
                cleaned_row = []
                for cell in row:
                    if cell is not None:
                        cleaned_row.append(str(cell).strip())
                    else:
                        cleaned_row.append("")

                if any(cell for cell in cleaned_row):
                    sheet_text += " | ".join(cleaned_row) + "\n"

            sheet_text += "\n"
            all_text.append(sheet_text)

        workbook.close()
        return "\n".join(all_text)

    except Exception as e:
        return f"Error reading Excel file: {str(e)}"


def extract_structured_data_from_excel(file_path: str) -> Dict[str, Any]:
    """
    Extract structured data from an Excel file for programmatic use.

    Args:
        file_path: Path to the Excel file

    Returns:
        Dict containing structured data from all sheets
    """
    try:
        structured_data = {}
        workbook = openpyxl.load_workbook(file_path, data_only=True)

        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]
            sheet_data = []

            # Get all rows with data
            rows_with_data = []
            for row in worksheet.iter_rows(values_only=True):
                if any(cell is not None and str(cell).strip() for cell in row):
                    rows_with_data.append(row)

            if not rows_with_data:
                structured_data[sheet_name] = []
                continue

            # Use first row as headers
            headers = rows_with_data[0] if rows_with_data else []
            data_rows = rows_with_data[1:] if len(rows_with_data) > 1 else []

            # Clean headers
            cleaned_headers = []
            for i, header in enumerate(headers):
                if header is not None and str(header).strip():
                    cleaned_headers.append(str(header).strip())
                else:
                    cleaned_headers.append(f"Column_{i+1}")

            # Convert rows to dictionaries
            for row in data_rows:
                row_dict = {}
                for i, cell in enumerate(row):
                    if i < len(cleaned_headers):
                        if cell is not None:
                            row_dict[cleaned_headers[i]] = str(cell).strip()
                        else:
                            row_dict[cleaned_headers[i]] = ""

                if any(value for value in row_dict.values()):
                    sheet_data.append(row_dict)

            structured_data[sheet_name] = sheet_data

        workbook.close()
        return structured_data

    except Exception as e:
        return {"error": f"Error reading Excel file: {str(e)}"}
