# Shipment Document Processor

A production-ready application that processes shipment documents (PDFs and Excel files) and extracts key data using Claude AI. Features a React frontend with Tailwind CSS and FastAPI backend.

## Features

- 📄 **Document Processing**: Supports PDF (including scanned) and Excel files
- 🤖 **AI-Powered Extraction**: Uses Claude AI to extract shipment data
- 📝 **Editable Forms**: Review and edit extracted data
- 👁️ **Document Preview**: View processed documents alongside extracted data
- 🎨 **Modern UI**: React frontend with Tailwind CSS
- 🚀 **Production Ready**: FastAPI backend with proper error handling

## Extracted Fields

- Bill of Lading Number
- Container Number
- Consignee Name & Address
- Date (MM/DD/YYYY format)
- Line Items Count
- Average Gross Weight
- Average Price

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation & Development

```bash
# Install all dependencies
make install

# Run both backend and frontend in development mode
make dev

# Or run servers separately:
make dev-backend    # Backend at http://localhost:8000
make dev-frontend   # Frontend at http://localhost:3000
```

### Environment Setup

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Available Make Commands

```bash
make help           # Show all available commands
make install        # Install Python and Node.js dependencies
make dev            # Run both servers concurrently
make dev-backend    # Run only FastAPI backend
make dev-frontend   # Run only React frontend
make build          # Build React app for production
make test           # Run Python tests
make clean          # Clean build artifacts
make test-api       # Test API endpoint
```

## API Documentation

Once the backend is running, visit:

- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Project Structure

```
├── app/
│   ├── frontend/          # React frontend with Tailwind CSS
│   ├── api/              # FastAPI routes
│   ├── core/             # Configuration
│   ├── models/           # Pydantic data models
│   ├── services/         # Business logic (LLM, document processing)
│   └── utils/            # Utility functions (PDF, XLSX processing)
├── test_files/           # Sample documents for testing
├── tests/                # Python unit tests
├── requirements.txt      # Python dependencies
└── Makefile             # Development workflow commands
```

## Testing

The application includes comprehensive test coverage:

```bash
# Run all Python tests
make test

# Test individual components
pytest tests/test_document_processor.py -v
```

## Production Deployment

```bash
# Build frontend for production
make build

# The built frontend will be in app/frontend/build/
```

## Docker Support

```bash
# Build Docker image
docker build -t shipment-processor .

# Run with Docker
docker run -d -p 8000:8000 shipment-processor
```
