# Document Processing Application

This API processes shipment documents and data is made readily available to user on UI

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the API: `python -m app.main`
4. You may access the API docs at [`http://localhost:8000/docs`](http://localhost:8000/docs)

### OCR prerequisites (optional but recommended)
For scanned PDFs, OCR improves extraction.

- macOS (Homebrew):
  - `brew install tesseract poppler`
- Ubuntu/Debian:
  - `sudo apt-get update && sudo apt-get install -y tesseract-ocr poppler-utils`

Python libs are installed from `requirements.txt` (Pillow, pdf2image, pytesseract).

Environment toggles:
- `OCR_ENABLED=true|false` (default true)
- `OCR_DPI=300` (rendering resolution)
- `OCR_KEEP_IMAGES=false` (set to true to keep intermediate PNGs in a temp folder for debugging)

## API Endpoints

- `POST /process-documents`: Single endpoint to process all documents and fill out the form
## Docker

### API only

Build the API image:

```bash
docker build -t document-processor-api .
```

Run the API container:

```bash
docker run -d -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_key_here \
  -e ANTHROPIC_API_KEY=your_anthropic_key_here \
  -e OCR_ENABLED=true \
  --name document-api document-processor-api
```

### Full stack with docker-compose

This repo includes a `docker-compose.yml` that builds and runs both services:

```bash
OPENAI_API_KEY=your_openai_key_here \
ANTHROPIC_API_KEY=your_anthropic_key_here \
OCR_ENABLED=true \
docker compose up --build
```

Services:
- API: http://localhost:8000 (FastAPI docs at /docs)
- Frontend: http://localhost:3000

The frontend uses `NEXT_PUBLIC_API_BASE_URL` to call the API over the internal
Docker network (`http://api:8000`).

## Testing


Run tests:

```bash
    pytest
```

## Evaluation

Run the evaluation script:

```bash
    python evaluation.py
```
