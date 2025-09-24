# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multimodal OCR application that extracts text from images and provides intelligent descriptions using local Ollama models via FastAPI backend and React frontend. The project is built as a full-stack application with a focus on local inference using Ollama's multimodal capabilities (moondream:1.8b, llava, llama3.2-vision) with smart OCR + Description mode.

## Architecture

### Frontend (`frontend/` directory)
- **Framework**: React 18 with TypeScript and Vite
- **UI Library**: shadcn/ui components with Radix UI primitives
- **Styling**: Tailwind CSS with custom theme extensions
- **State Management**: React Query (@tanstack/react-query) for server state
- **Theme**: Dark/light mode support via next-themes
- **Routing**: React Router DOM with single-page architecture

### Key Components Architecture
- **Index** (`src/pages/Index.tsx`): Main page orchestrating file upload and text extraction
- **UploadZone** (`src/components/UploadZone.tsx`): Drag-and-drop file upload with preview and validation
- **ResultPanel** (`src/components/ResultPanel.tsx`): Displays extraction results with copy functionality
- **Header** (`src/components/Header.tsx`): App header with branding

### Backend (`backend/` directory)
- **Framework**: FastAPI with Python 3.11+
- **HTTP Client**: httpx for async Ollama communication
- **Validation**: Pydantic for request/response models
- **Image Processing**: Pillow + python-magic for validation
- **Configuration**: pydantic-settings with .env support
- **AI Integration**: Local Ollama multimodal models

### Key Backend Components
- **main.py**: FastAPI application with CORS and endpoints
- **config.py**: Environment-based configuration management
- **ollama_client.py**: Async Ollama API client with fallback logic
- **image_utils.py**: Image validation, MIME detection, base64 encoding
- **schemas.py**: Pydantic models for API responses
- **errors.py**: Custom exception handling with structured responses

### Data Flow
1. User uploads image via UploadZone component
2. File validation (PNG, JPEG, WebP up to 10MB) on frontend
3. API call to FastAPI backend at `http://localhost:8000/api/extract-text`
4. Backend validates file type/size using magic bytes
5. Image converted to base64 and sent to Ollama
6. Ollama processes with multimodal models (llava/moondream/llama3.2-vision)
7. Extracted text returned to frontend via structured JSON response
8. Results displayed in ResultPanel with model info and token usage

## Development Commands

### Prerequisites Setup
```bash
# Install Ollama (required for local development)
# macOS:
brew install ollama
# or visit: https://ollama.ai

# Start Ollama service
ollama serve

# Pull a multimodal model (choose one)
ollama pull llava         # ~4GB, good balance
ollama pull moondream     # ~1.6GB, faster
ollama pull llama3.2-vision  # ~7GB, best quality
```

### Frontend Development
```bash
cd frontend
npm i                    # Install dependencies
npm run dev             # Start development server on port 8080
npm run build           # Production build
npm run build:dev       # Development build
npm run lint            # Run ESLint
npm run preview         # Preview production build
```

### Backend Development
```bash
cd backend
pip install -e .        # Install dependencies (uses pyproject.toml)
uvicorn app.main:app --reload  # Start development server on port 8000
pytest tests/           # Run tests
black app/              # Format code (line-length: 88, target: py311)
mypy app/               # Type checking (strict mode enabled)
isort app/              # Sort imports (black profile)
```

### Full Stack Development
```bash
# Terminal 1: Start Ollama
ollama serve
ollama pull llava       # Download multimodal model

# Terminal 2: Start Backend
cd backend && uvicorn app.main:app --reload

# Terminal 3: Start Frontend
cd frontend && npm run dev

# Terminal 4: Test Integration
python test_integration.py
```

### Docker Development
```bash
docker-compose up --build    # Start all services (backend:8000, frontend:8080, ollama:11434)
docker-compose exec ollama ollama pull llava  # Download model (or moondream/llama3.2-vision)
docker-compose logs backend  # View backend logs
docker-compose logs -f backend  # Follow backend logs
docker-compose down         # Stop all services
docker-compose ps           # Check service status
```

## Configuration

### Path Aliases
The project uses TypeScript path mapping configured in `components.json`:
- `@/components` → `src/components`
- `@/lib` → `src/lib`
- `@/hooks` → `src/hooks`
- `@/ui` → `src/components/ui`

### Theme System
- Uses CSS variables for theming defined in `src/index.css`
- Custom upload-specific colors in Tailwind config
- Supports system/light/dark theme modes

### Build Configuration
- Vite configured with React SWC plugin for fast compilation
- Development server runs on `::` (all interfaces) port 8080
- Lovable-tagger integration for component tagging in development

## Backend Configuration

### Environment Variables
Backend configuration via `.env` file:
```bash
OLLAMA_HOST=http://localhost:11434        # Ollama server URL
OLLAMA_MODEL=llava                        # Model name (llava/moondream/llama3.2-vision)
REQUEST_TIMEOUT_MS=60000                  # Request timeout
MAX_UPLOAD_MB=10                          # File size limit
ALLOWED_IMAGE_MIME=image/png,image/jpeg,image/webp  # Allowed file types
ALLOWED_ORIGINS=http://localhost:8080,http://localhost:3000  # CORS origins
HOST=0.0.0.0                             # Server host
PORT=8000                                # Server port
```

### API Endpoints
- `GET /` - Basic API information
- `GET /healthz` - Health check with Ollama connectivity status
- `POST /api/extract-text` - Text extraction endpoint
- `GET /docs` - Swagger API documentation
- `GET /redoc` - ReDoc API documentation

### Ollama Integration
- Supports `/api/chat` endpoint (preferred) with automatic fallback to `/api/generate`
- System prompt enforces text-only extraction without commentary
- Handles model errors, timeouts, and connection issues
- Response parsing removes code fences and common AI prefixes

## File Structure Conventions

```
multimodal-ocr-textract-ollama/
├── frontend/src/
│   ├── components/           # Reusable UI components
│   │   ├── ui/              # shadcn/ui components
│   │   ├── Header.tsx       # App header
│   │   ├── UploadZone.tsx   # File upload component
│   │   └── ResultPanel.tsx  # Results display component
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utility functions
│   ├── pages/              # Page components
│   │   ├── Index.tsx       # Main application page
│   │   └── NotFound.tsx    # 404 page
│   └── App.tsx             # Root application component
├── backend/app/
│   ├── main.py             # FastAPI application
│   ├── config.py           # Configuration management
│   ├── ollama_client.py    # Ollama API client
│   ├── image_utils.py      # Image processing utilities
│   ├── schemas.py          # Pydantic models
│   └── errors.py           # Custom exceptions
├── backend/tests/          # Backend tests
├── docker-compose.yml      # Container orchestration
└── test_integration.py     # Integration testing
```

## Development Notes

### Frontend
- Uses strict TypeScript configuration with module resolution
- ESLint configured with React-specific rules
- Project originally created with Lovable platform integration
- Ready for local development and deployment
- API calls updated to use real backend at `http://localhost:8000`

### Backend
- FastAPI with async/await patterns for performance
- Pydantic for request/response validation and serialization
- Memory-only processing - no files stored to disk
- Comprehensive error handling with structured responses
- Docker support with multi-stage builds for production
- Health checks for both API and Ollama connectivity
- Package management via pyproject.toml with optional dev dependencies
- Code formatting enforced with black (line-length: 88) and isort
- Type checking with mypy in strict mode

### AI Integration
- Designed to work with local Ollama instance at `localhost:11434`
- Supports multiple multimodal models (llava, moondream, llama3.2-vision)
- Automatic fallback between Ollama API endpoints
- System prompts engineered for clean text extraction
- Token usage tracking when available from models

### Testing
- Backend unit tests with pytest and mocking
- Integration test script for full-stack verification
- Docker health checks for all services
- API documentation with Swagger/OpenAPI

### Security
- CORS configured for allowed origins only
- File type validation using magic bytes (not just extensions)
- Size limits enforced (10MB max)
- No persistent file storage
- Error messages provide helpful guidance without exposing internals