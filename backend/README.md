# Ollama OCR Backend

FastAPI backend for extracting text from images using local Ollama multimodal models.

## Features

- 📷 Support for PNG, JPEG, and WebP images (up to 10MB)
- 🤖 Local inference using Ollama multimodal models (llava, moondream, llama3.2-vision)
- 🔒 Memory-only processing (no disk storage)
- 🚀 Async processing with proper error handling
- 🐳 Docker support with multi-stage builds
- ⚡ Automatic API fallback (/api/chat → /api/generate)

## Quick Start

### Prerequisites

1. **Python 3.11+** installed
2. **Ollama** running locally at `http://localhost:11434`
3. A multimodal model downloaded, e.g.:
   ```bash
   ollama pull llava
   # or
   ollama pull moondream
   # or
   ollama pull llama3.2-vision
   ```

### Local Development

1. **Clone and setup**:
   ```bash
   cd backend
   pip install -e .
   ```

2. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env to customize settings
   ```

3. **Run the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

4. **Test the API**:
   ```bash
   # Health check
   curl http://localhost:8000/healthz

   # Extract text from image
   curl -X POST "http://localhost:8000/api/extract-text" \
     -F "file=@path/to/your/image.jpg"
   ```

### Docker Deployment

1. **Build and run with Docker Compose** (recommended):
   ```bash
   # From project root
   docker-compose up --build
   ```

   This starts:
   - Backend API at `http://localhost:8000`
   - Ollama service at `http://localhost:11434`
   - Frontend at `http://localhost:8080`

2. **Or build backend only**:
   ```bash
   cd backend
   docker build -t ollama-ocr-backend .
   docker run -p 8000:8000 \
     -e OLLAMA_HOST=http://host.docker.internal:11434 \
     ollama-ocr-backend
   ```

## API Documentation

### Endpoints

#### `GET /`
Basic information about the API.

#### `GET /healthz`
Health check endpoint that verifies Ollama connectivity.

#### `POST /api/extract-text`
Extract text from uploaded image.

**Request:**
- `file`: Image file (multipart/form-data)
- Supported formats: PNG, JPEG, WebP
- Max size: 10MB

**Response:**
```json
{
  "text": "Extracted text content...",
  "model": "llava",
  "usage": {
    "prompt_tokens": 45,
    "completion_tokens": 120,
    "total_tokens": 165
  }
}
```

**Error Response:**
```json
{
  "error": "ImageValidationError",
  "message": "File size must be less than 10MB",
  "code": 400
}
```

### Error Codes

- `400`: Invalid file (size, type, corruption)
- `503`: Ollama not reachable or model missing
- `504`: Request timeout
- `500`: Internal server error

## Configuration

Configure via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llava` | Model name to use |
| `REQUEST_TIMEOUT_MS` | `60000` | Request timeout in milliseconds |
| `MAX_UPLOAD_MB` | `10` | Maximum file size in MB |
| `ALLOWED_IMAGE_MIME` | `image/png,image/jpeg,image/webp` | Allowed MIME types |
| `ALLOWED_ORIGINS` | `http://localhost:8080,http://localhost:3000` | CORS origins |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |

## Supported Models

The backend supports any Ollama multimodal model. Popular choices:

- **llava** - General purpose, good accuracy
- **moondream** - Lightweight, fast inference
- **llama3.2-vision** - Latest Meta model

Pull models with:
```bash
ollama pull <model-name>
```

## Development

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration management
│   ├── schemas.py        # Pydantic models
│   ├── errors.py         # Custom exceptions
│   ├── image_utils.py    # Image validation & processing
│   └── ollama_client.py  # Ollama API client
├── tests/                # Test files
├── Dockerfile           # Container build
├── pyproject.toml       # Dependencies
└── README.md
```

### Adding Tests

```bash
pip install -e ".[dev]"
pytest tests/
```

### Code Quality

```bash
# Format code
black app/
isort app/

# Type checking
mypy app/
```

## Troubleshooting

### Common Issues

1. **"Cannot connect to Ollama"**
   - Ensure Ollama is running: `ollama serve`
   - Check if model is available: `ollama list`
   - Verify host URL in configuration

2. **"Model not found"**
   - Pull the required model: `ollama pull llava`
   - Check model name in configuration

3. **File validation errors**
   - Ensure file is a valid image
   - Check file size (max 10MB)
   - Verify file type (PNG/JPEG/WebP only)

4. **Docker networking issues**
   - Use `host.docker.internal` instead of `localhost` in Docker
   - Check if ports are properly exposed

### Debugging

Enable debug logging:
```python
import logging
logging.getLogger("app").setLevel(logging.DEBUG)
```

## License

MIT License - see project root for details.