from app.services import document_processor as dp
import app.utils.text_utils as text_utils

from app.services.llm_service import extract_fields_from_document
from app.services.form_filler import fill_form


# FPS = ['documents/BillOfLading.pdf']
FPS = ['documents/BillOfLading.pdf', 'documents/InvoicePackingList.xlsx']
# FPS = ['documents/InvoicePackingList.xlsx']


# print(extract_text_from_pdf(FPS[1]))
textDataResp = dp.process_documents(FPS)
# print(f"LLM Output: {textDataResp}\n\n\n")

fields = [
    'Bill of lading number',
    'Container Number',
    'Consignee Name',
    'Consignee Address',
    'Line Items Count',
    # 'Date' - populated programatically
    'Weight', # Changed to 'Average Gross Weight' after LLM processing.
    'Price' # # Changed to 'Average Gross Weight' after LLM processing.
]

fieldsJSON = extract_fields_from_document(textDataResp, fields)
print(fieldsJSON)

success = fill_form(fieldsJSON)
print("Form submitted successfully!" if success else "Form submission failed.")