# Shipment Document Processing Platform

A production-ready web application that automatically extracts shipment data from trade documents using AI. The system processes Bills of Lading (PDFs) and Invoice/Packing Lists (Excel files) to extract key shipping information.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Technical Details](#technical-details)
- [Docker Deployment](#docker-deployment)

## Overview

This platform automates the extraction of shipment data from various trade documents by:
1. Accepting multiple document uploads (PDFs and Excel files)
2. Processing documents using advanced OCR and text extraction
3. Analyzing all documents collectively using Anthropic's Claude AI
4. Extracting specific fields like Bill of Lading number, Container number, Consignee information, etc.
5. Presenting extracted data in an editable form with document preview

## Features

### Core Functionality
- **Multi-Document Processing**: Handles any number of PDFs and Excel files simultaneously
- **Intelligent Extraction**: Uses Claude AI to understand and extract data from various document formats
- **Image PDF Support**: Processes both text-based and image-based PDFs using OCR
- **Excel Preview**: In-browser preview of Excel files with sheet navigation
- **Document Viewer**: Side-by-side document viewing for easy verification
- **Editable Forms**: Extracted data can be manually corrected if needed
- **Cross-Document Analysis**: Combines information from multiple documents to complete all fields

### Extracted Fields
1. **Bill of Lading Number**
2. **Container Number**
3. **Consignee Name** (receiver/buyer)
4. **Consignee Address**
5. **Date** (shipment/invoice date)
6. **Line Items Count** (total pieces/packages)
7. **Average Gross Weight**
8. **Average Price**

## Architecture

```
┌─────────────────────────────────────────────┐
│           Frontend (React + TypeScript)       │
│                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Document │  │ Shipment │  │ Document │  │
│  │ Uploader │  │   Form   │  │  Viewer  │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└───────────────────────┬──────────────────────┘
                        │ HTTP/API
                        │
┌───────────────────────▼──────────────────────┐
│              Nginx Reverse Proxy              │
│         (Routes /api to backend:8000)         │
└───────────────────────┬──────────────────────┘
                        │
┌───────────────────────▼──────────────────────┐
│           Backend (FastAPI + Python)          │
│                                               │
│  ┌──────────────────────────────────────┐   │
│  │         Document Processor           │   │
│  │  ┌─────────┐  ┌─────────────────┐  │   │
│  │  │   PDF   │  │      Excel      │  │   │
│  │  │  Utils  │  │     Utils       │  │   │
│  │  └─────────┘  └─────────────────┘  │   │
│  └──────────────────────────────────────┘   │
│                                               │
│  ┌──────────────────────────────────────┐   │
│  │          LLM Service                 │   │
│  │    (Anthropic Claude Integration)    │   │
│  └──────────────────────────────────────┘   │
└───────────────────────────────────────────────┘
```

## How It Works

### Step 1: Document Upload
1. User accesses the web interface at `http://localhost`
2. Drag and drop or click to select multiple documents
3. Supported formats:
   - PDF files (Bills of Lading, shipping documents)
   - Excel files (.xlsx, .xls) for Invoices and Packing Lists
4. Files are uploaded to the backend via multipart form data

### Step 2: Document Processing

#### PDF Processing
```python
# app/utils/pdf_utils.py
def extract_text_from_pdf(file_path):
    # 1. Try PyPDF2 for text extraction
    # 2. If no text, try PyMuPDF
    # 3. If still no text, mark as image PDF
    # 4. For image PDFs, convert pages to PNG images
```

**Text-based PDFs:**
- Extracts text using PyPDF2 and PyMuPDF libraries
- Preserves formatting and structure

**Image-based PDFs:**
- Detects when PDF contains embedded images instead of text
- Converts PDF pages to high-resolution PNG images
- Encodes images as base64 for AI processing

#### Excel Processing
```python
# app/utils/xlsx_utils.py
def extract_data_from_xlsx(file_path):
    # 1. Load workbook with openpyxl
    # 2. Iterate through all sheets
    # 3. Extract all rows as lists
    # 4. Return structured data by sheet
```

- Reads all sheets in the workbook
- Preserves cell values and structure
- Handles multiple sheets (Invoice, Packing List, etc.)

### Step 3: AI-Powered Extraction

The system sends all documents to Claude AI with specific instructions:

```python
# app/services/llm_service.py
def extract_shipment_data(documents):
    # 1. Prepare document content
    #    - Text from text-based PDFs
    #    - Images from image-based PDFs
    #    - Structured data from Excel files
    
    # 2. Create comprehensive prompt
    #    - Instructions for each field
    #    - Examples of where to find data
    #    - Rules for extraction
    
    # 3. Send to Claude API
    #    - Model: claude-sonnet-4-20250514
    #    - Temperature: 0 (deterministic)
    #    - Analyzes all documents together
    
    # 4. Parse JSON response
    #    - Validate extracted fields
    #    - Return structured data
```

**Key Extraction Logic:**
- **Bill of Lading Number**: Searches for "B/L NO", "BOL", etc.
- **Container Number**: Looks for "CNTR NO", "Container Number"
- **Consignee**: Identifies receiver (NOT shipper) from "CONSIGNEE", "SHIP TO", "BUYER"
- **Line Items**: Counts total pieces or individual product rows
- **Calculations**: Computes averages for weight and price

### Step 4: Data Presentation

1. **Shipment Form**
   - Displays all extracted fields
   - Fields are editable for manual correction
   - Real-time validation
   - Save functionality

2. **Document Viewer**
   - PDF Preview: Embedded iframe or download option
   - Excel Preview: HTML table with sheet navigation
   - Navigation between multiple documents
   - Download original files

### Step 5: Data Storage

```python
# In-memory storage for session
document_storage = {
    "session_id_0": {
        "content": base64_encoded_file,
        "filename": "original_name.pdf",
        "content_type": "application/pdf"
    }
}
```

## Installation

### Prerequisites
- Docker and Docker Compose
- Anthropic API Key

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd project-boilerplate
```

2. **Ensure API key is configured**
The API key is already set in `docker-compose.yml`:
```yaml
environment:
  - ANTHROPIC_API_KEY=sk-ant-api03-...
```

3. **Build and run with Docker**
```bash
# Build Docker images
docker-compose build

# Start the application
docker-compose up -d

# Check status
docker-compose ps
```

4. **Access the application**
Open browser to: `http://localhost`

### Manual Installation (Development)

1. **Backend Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run backend
cd app
python main.py
```

2. **Frontend Setup**
```bash
# Install Node dependencies
cd frontend
npm install

# Run frontend
npm start
```

## Usage

### Basic Workflow

1. **Upload Documents**
   - Click or drag files to upload area
   - Select multiple files at once
   - Wait for processing (usually 5-10 seconds)

2. **Review Extracted Data**
   - Check each field for accuracy
   - Edit any incorrect values
   - Fields show as "null" if not found

3. **Verify with Document Viewer**
   - Use navigation arrows to switch between documents
   - Compare extracted data with original documents
   - Download documents if needed

### Example Documents

Test files included:
- `BL-COSU534343282.pdf` - Bill of Lading (image-based PDF)
- `Demo-Invoice-PackingList_1 (1).xlsx` - Invoice and Packing List

Expected extraction:
```json
{
  "bill_of_lading_number": "ZMLU34110002",
  "container_number": "MSCU1234567",
  "consignee_name": "KABOFER TRADING INC",
  "consignee_address": "66-89 MAIN ST 36H 643, FLUSHING, NY, 94089 US",
  "date": "2019-08-22",
  "line_items_count": 18,
  "average_gross_weight": "162.38 KG",
  "average_price": "1289.51 USD"
}
```

## API Documentation

### POST /process-documents
Upload and process multiple documents.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Multiple files

**Response:**
```json
{
  "status": "success",
  "shipment_data": {
    "bill_of_lading_number": "string",
    "container_number": "string",
    "consignee_name": "string",
    "consignee_address": "string",
    "date": "string",
    "line_items_count": "number",
    "average_gross_weight": "string",
    "average_price": "string"
  },
  "metadata": {
    "total_files_processed": 2,
    "pdf_count": 1,
    "excel_count": 1
  },
  "document_ids": ["session_0", "session_1"]
}
```

### GET /document/{document_id}/base64
Retrieve a document for preview.

**Response:**
```json
{
  "content": "base64_encoded_content",
  "content_type": "application/pdf",
  "filename": "document.pdf",
  "excel_preview": {}  // Optional, for Excel files
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Document Processing API"
}
```

## Project Structure

```
project-boilerplate/
├── app/                        # Backend application
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── core/
│   │   └── config.py          # Configuration
│   ├── services/
│   │   ├── document_processor.py  # Document processing logic
│   │   └── llm_service.py        # AI extraction service
│   ├── utils/
│   │   ├── pdf_utils.py      # PDF processing utilities
│   │   └── xlsx_utils.py     # Excel processing utilities
│   └── main.py                # FastAPI application
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentUploader.tsx    # Upload interface
│   │   │   ├── ShipmentForm.tsx       # Data display form
│   │   │   ├── DocumentViewerSimple.tsx # Document preview
│   │   │   └── ExcelPreview.tsx       # Excel viewer
│   │   ├── types.ts          # TypeScript types
│   │   ├── config.ts         # Frontend config
│   │   └── App.tsx           # Main application
│   └── package.json
│
├── docker-compose.yml         # Docker orchestration
├── backend.Dockerfile        # Backend container
├── frontend.Dockerfile       # Frontend container
├── nginx.conf               # Web server config
└── requirements.txt         # Python dependencies
```

## Technical Details

### Backend Technologies
- **FastAPI**: High-performance Python web framework
- **Uvicorn**: ASGI server with multiple workers
- **PyPDF2 & PyMuPDF**: PDF text extraction
- **OpenPyXL**: Excel file processing
- **Anthropic SDK**: Claude AI integration
- **Pydantic**: Data validation and settings

### Frontend Technologies
- **React 18**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Axios**: HTTP client
- **React Dropzone**: File upload
- **Lucide React**: Icons
- **CSS3**: Styling

### AI Model
- **Model**: Claude Sonnet (claude-sonnet-4-20250514)
- **Capabilities**: 
  - Multimodal (text + images)
  - Document understanding
  - Data extraction
  - Cross-document analysis
- **Configuration**:
  - Temperature: 0 (deterministic)
  - Max tokens: 1000
  - Context window: Handles multiple documents

### Document Processing Pipeline

1. **File Reception**
   - Multipart upload handling
   - File type validation
   - Temporary storage

2. **Content Extraction**
   - Text extraction (PDFs)
   - Image extraction (scanned PDFs)
   - Structured data extraction (Excel)

3. **AI Analysis**
   - Document aggregation
   - Prompt engineering
   - Field extraction
   - Validation

4. **Response Generation**
   - JSON formatting
   - Session management
   - Document storage

## Docker Deployment

### Container Architecture
```yaml
services:
  backend:
    - Python 3.11 slim
    - FastAPI application
    - 4 worker processes
    - Port 8000 (internal)
    
  frontend:
    - Node 18 (build)
    - Nginx Alpine (serve)
    - Port 80 (exposed)
    - Proxies /api to backend
```

### Volumes
- `temp_files`: Temporary file storage
- `logs`: Application logs

### Networks
- `shipment-network`: Bridge network for container communication

### Commands
```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart
```

## Troubleshooting

### Common Issues

1. **"Failed to process documents"**
   - Check API key in docker-compose.yml
   - Verify backend is running: `docker-compose ps`
   - Check logs: `docker-compose logs backend`

2. **PDF not extracting**
   - May be image-based PDF
   - System automatically handles via OCR
   - Check if PyMuPDF is installed

3. **Excel preview not working**
   - Verify file format (.xlsx, .xls)
   - Check browser console for errors
   - Try downloading and opening locally

4. **Container won't start**
   - Check port 80 is available
   - Verify Docker is running
   - Check disk space

### Debug Commands
```bash
# Check container status
docker-compose ps

# View backend logs
docker-compose logs backend -f

# Test API health
curl http://localhost/api/health

# Rebuild after changes
docker-compose build --no-cache
```

## Performance Considerations

- **File Size Limits**: 50MB per file (configurable in nginx.conf)
- **Processing Time**: ~5-10 seconds for typical documents
- **Concurrent Users**: 4 worker processes handle multiple requests
- **Memory Usage**: ~500MB baseline, scales with document size
- **API Rate Limits**: Subject to Anthropic API limits

## Security Notes

- API key is stored in environment variables
- File uploads are validated by type
- Temporary files are isolated in Docker volumes
- CORS configured for production use
- Security headers in Nginx configuration

## License

This project is proprietary and confidential.

## Support

For issues or questions, please contact the development team.
