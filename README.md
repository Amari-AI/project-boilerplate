# Document Processing Application

Full-stack document processing application with FastAPI backend and Next.js frontend. Processes shipment documents (PDF,
Excel) using AI and provides a web interface for data extraction.

## Architecture

- **Backend**: FastAPI application (Python) - Document processing and AI integration
- **Frontend**: Next.js 15 application (TypeScript) - Web UI with shadcn/ui components

## Quick Start with Docker (Project: anchor)

1. Clone the repository.
2. Copy the environment template:
   cp .env.example .env
3. Open the .env file and add your Anthropic API key.
4. Start both services with Docker in detached mode (using project name "anchor"):

   ```bash
   docker-compose -p anchor up --build -d
   ```

5. Monitor the logs of your running containers:

   ```bash
   docker-compose -p anchor logs --follow
   ```

6. When you're done, stop and clean up all services, networks, and volumes with:

   ```bash
   docker-compose -p anchor down --volumes --remove-orphans
   ```

   If you want to just stop the services, you can run:
   ```bash
   docker-compose -p anchor down
   ```

After these steps, you'll have:

- The Frontend App running at http://localhost:3000
- The Backend API running at http://localhost:8000
    - API docs available at http://localhost:8000/docs

## Development Setup

### Backend (FastAPI)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python -m app.main

# Run tests
pytest

# Run evaluation script
python evaluation.py
```

### Frontend (Next.js)

```bash
# Navigate to web directory
cd web

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## API Endpoints

- `POST /process-documents`: Process uploaded documents and extract structured data

## Environment Variables

- `ANTHROPIC_API_KEY`: Anthropic Claude API key for document processing
- `NEXT_PUBLIC_API_URL`: Backend API URL (http://localhost:8000 for local development)

## Docker Services

- `backend`: FastAPI application container
- `frontend`: Next.js application container
- Shared network for service communication
- Volume mounting for file uploads
