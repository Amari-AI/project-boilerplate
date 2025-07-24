# Document Processing App with React UI

This document processing app now includes a modern React-like UI that allows users to upload documents, process them, and edit the extracted data.

## Features

1. **File Upload**: Drag-and-drop or click to upload PDF and Excel files
2. **Document Processing**: Automatically extracts invoice and bill of lading data
3. **Data Editing**: View and edit extracted data in a friendly format
4. **Side Panel**: Shows all uploaded documents with file information
5. **Data Export**: Download extracted data as JSON

## Quick Start

### Option 1: Using the Built-in HTML UI (Recommended)

The app includes a pre-built HTML/CSS/JavaScript UI that works immediately without requiring Node.js:

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the FastAPI server:
   ```bash
   python app/main.py
   ```

3. Open your browser and go to `http://localhost:8000`

The HTML UI provides all the same functionality as a React app but doesn't require any build process.

### Option 2: Using React (Requires Node.js)

If you have Node.js installed and want to use the React version:

1. Install Node.js from https://nodejs.org/

2. Install React dependencies:
   ```bash
   cd frontend
   npm install
   ```

3. Build the React app:
   ```bash
   npm run build
   ```

4. Start the FastAPI server:
   ```bash
   cd ..
   python app/main.py
   ```

5. Open your browser and go to `http://localhost:8000`

## How to Use

1. **Upload Documents**: 
   - Drag and drop PDF or Excel files into the upload area
   - Or click the upload area to browse and select files
   - Supported formats: PDF (.pdf), Excel (.xlsx)

2. **Process Documents**:
   - Click the "Process Documents" button after uploading
   - The app will extract invoice data from Excel files and bill of lading data from PDFs
   - Processing may take a few moments

3. **View and Edit Data**:
   - Extracted data appears in editable forms
   - Invoice items can be added or removed
   - All fields can be modified

4. **Manage Files**:
   - View uploaded files in the right panel
   - Remove files by clicking the × button
   - See file sizes and types

5. **Export Data**:
   - Click "Download JSON" to save extracted data
   - Data is saved in JSON format for further processing

## API Endpoints

- `GET /`: Serves the UI (HTML file or React app)
- `POST /process-documents`: Processes uploaded files and returns extracted data

## UI Components

- **FileUpload**: Handles file uploads with drag-and-drop
- **DataEditor**: Displays and allows editing of extracted data
- **DocumentPanel**: Shows uploaded files in a sidebar
- **Processing Indicator**: Shows loading state during processing

## Backend Changes

Minimal changes were made to the existing backend:

1. Updated `app/main.py` to serve static files and the UI
2. Added `aiofiles` dependency for static file serving
3. Modified the root endpoint to serve the HTML UI

The existing `/process-documents` endpoint remains unchanged and fully functional.

## File Structure

```
project-boilerplate/
├── app/                     # Existing FastAPI backend
├── frontend/
│   ├── build/
│   │   └── index.html      # Built HTML UI (ready to use)
│   ├── src/                # React source files (optional)
│   └── package.json        # React dependencies
└── README_UI.md           # This file
```

## Troubleshooting

### "React UI not built yet" message
- Make sure the `frontend/build/index.html` file exists
- If using React, run `npm run build` in the frontend directory

### Upload not working
- Check that files are PDF (.pdf) or Excel (.xlsx) format
- Ensure the FastAPI server is running on port 8000

### Processing fails
- Verify your API keys are set in the environment
- Check the console for error messages
- Ensure uploaded files contain extractable data

## Development

To modify the UI:

1. **HTML Version**: Edit `frontend/build/index.html` directly
2. **React Version**: Edit files in `frontend/src/` and run `npm run build`

The HTML version is self-contained and easier to modify for quick changes. 