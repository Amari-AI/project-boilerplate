from fastapi import FastAPI, UploadFile, File, HTTPException
from app.api.routes import router
from app.services import document_processor as dp
from app.services.llm_service import extract_fields_from_document
from app.services.form_filler import fill_form
import uvicorn
from typing import List

app = FastAPI(title="Document Processing API")

# Including the router for other API routes
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Document Processing API"}

# New endpoint for document processing and form filling
@app.post("/process-form/")
async def process_and_fill_form(files: List[UploadFile] = File(...)):
    # Step 1: Process the uploaded files
    try:
        file_paths = []
        for file in files:
            file_path = f"temp_files/{file.filename}"
            with open(file_path, "wb") as f:
                f.write(await file.read())
            file_paths.append(file_path)
        
        # Step 2: Process documents
        textDataResp = dp.process_documents(file_paths)
        
        # Step 3: Define the fields you want to extract
        fields = [
            'Bill of lading number',
            'Container Number',
            'Consignee Name',
            'Consignee Address',
            'Line Items Count',
            'Weight',
            'Price',
        ]
        
        # Step 4: Extract the fields from the processed documents
        fieldsJSON = extract_fields_from_document(textDataResp, fields)

        # Step 5: Fill the form with extracted data
        success = fill_form(fieldsJSON)
        
        if success:
            return {"message": "Form submitted successfully!"}
        else:
            raise HTTPException(status_code=400, detail="Form submission failed.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
