# Multimodal OCR with Ollama

A full-stack web application for extracting text from images using local Ollama multimodal models. Built with FastAPI backend and React frontend, designed for privacy-focused, local AI inference.

## ✨ Features

- 🖼️ **Image Upload**: Drag & drop or click to upload PNG, JPEG, WebP images (up to 10MB)
- 🤖 **Local AI**: Uses local Ollama multimodal models (moondream:1.8b, llava, llama3.2-vision)
- 📝 **Smart OCR + Description**: Extracts text AND provides intelligent image descriptions
- 🔒 **Privacy First**: No data leaves your machine - all processing is local
- ⚡ **Extended Processing**: Handles complex images with up to 5-minute processing time
- 🎨 **Modern UI**: Clean, responsive interface built with React and shadcn/ui
- 🐳 **Docker Ready**: Full containerization with docker-compose
- 🔧 **Developer Friendly**: Hot reload, comprehensive error handling, API documentation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React         │    │   FastAPI       │    │   Ollama        │
│   Frontend      │───▶│   Backend       │───▶│   Models        │
│   (Port 8080)   │    │   (Port 8000)   │    │   (Port 11434)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

- **Frontend**: React 18 + TypeScript + Vite + shadcn/ui + Tailwind CSS
- **Backend**: FastAPI + Python 3.11+ + httpx + Pydantic
- **AI Runtime**: Ollama with multimodal models
- **Deployment**: Docker + docker-compose

## 🚀 Quick Start

### Prerequisites

1. **Docker & Docker Compose** (recommended) OR
2. **Node.js 18+**, **Python 3.11+**, and **Ollama** installed locally

### Option 1: Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd multimodal-ocr-textract-ollama
   ```

2. **Start all services**:
   ```bash
   docker-compose up --build
   ```

3. **Pull the Ollama model** (in another terminal):
   ```bash
   # Wait for services to start, then:
   docker-compose exec ollama ollama pull llava
   ```

4. **Access the application**:
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000
   - API docs: http://localhost:8000/docs

### Option 2: Local Development

#### 1. Setup Ollama

```bash
# Install Ollama (macOS)
brew install ollama

# Or follow instructions at: https://ollama.ai

# Start Ollama service
ollama serve

# Pull a multimodal model
ollama pull llava
```

#### 2. Setup Backend

```bash
cd backend

# Install dependencies
pip install -e .

# Optional: Configure environment
cp .env.example .env

# Start the backend
uvicorn app.main:app --reload
```

#### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### 4. Test the Integration

```bash
# From project root
python test_integration.py
```

## 📖 Usage

1. **Open the application** in your browser (http://localhost:8080)

2. **Upload an image**:
   - Drag & drop an image onto the upload zone, or
   - Click "Choose Image" to select a file
   - Supported formats: PNG, JPEG, WebP (max 10MB)

3. **Extract text**:
   - Click "Extract Text" to process the image
   - Wait for the local AI model to analyze the image
   - View the extracted text in the results panel

4. **Copy results**:
   - Use the "Copy" button to copy extracted text to clipboard
   - Text preserves original formatting and line breaks

## 🔧 Configuration

### Environment Variables

Create `.env` files to customize settings:

**Backend (`backend/.env`)**:
```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=moondream:1.8b
REQUEST_TIMEOUT_MS=300000
MAX_UPLOAD_MB=10
ALLOWED_IMAGE_MIME=image/png,image/jpeg,image/webp
ALLOWED_ORIGINS=http://localhost:8080,http://localhost:3000
HOST=0.0.0.0
PORT=8000
```

### Supported Models

The application works with any Ollama multimodal model:

| Model | Size | Speed | OCR + Description | Command |
|-------|------|-------|-------------------|---------|
| **moondream:1.8b** | ~1.6GB | Fast | Excellent | `ollama pull moondream:1.8b` |
| **llava** | ~4GB | Medium | Very Good | `ollama pull llava` |
| **llama3.2-vision** | ~7GB | Slow | Excellent | `ollama pull llama3.2-vision` |

Change the model by setting `OLLAMA_MODEL` in your `.env` file.

## 🛠️ Development

### Project Structure

```
multimodal-ocr-textract-ollama/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/       # UI components
│   │   ├── pages/           # Page components
│   │   ├── lib/             # Utilities
│   │   └── hooks/           # Custom hooks
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── config.py        # Configuration
│   │   ├── schemas.py       # Pydantic models
│   │   ├── errors.py        # Error handling
│   │   ├── image_utils.py   # Image processing
│   │   └── ollama_client.py # Ollama integration
│   ├── tests/               # Test files
│   └── pyproject.toml
├── docker-compose.yml       # Container orchestration
├── test_integration.py      # Integration tests
└── README.md
```

### Available Commands

**Frontend**:
```bash
cd frontend
npm run dev        # Development server
npm run build      # Production build
npm run lint       # ESLint
npm run preview    # Preview build
```

**Backend**:
```bash
cd backend
uvicorn app.main:app --reload  # Development server
pytest tests/                  # Run tests
black app/                     # Format code
mypy app/                      # Type checking
```

**Docker**:
```bash
docker-compose up --build     # Start all services
docker-compose down           # Stop all services
docker-compose logs backend   # View backend logs
```

### API Documentation

When the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Adding New Features

1. **Backend changes**: Modify files in `backend/app/`
2. **Frontend changes**: Modify files in `frontend/src/`
3. **Models**: Add new Ollama models by updating the configuration
4. **Tests**: Add tests in `backend/tests/` and run with `pytest`

## 🐛 Troubleshooting

### Common Issues

1. **"Cannot connect to Ollama"**
   ```bash
   # Make sure Ollama is running
   ollama serve

   # Check if model is available
   ollama list

   # Pull model if missing
   ollama pull llava
   ```

2. **"Backend not accessible"**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/healthz

   # Start backend manually
   cd backend && uvicorn app.main:app --reload
   ```

3. **"File too large" or validation errors**
   - Ensure image is < 10MB
   - Use supported formats: PNG, JPEG, WebP
   - Check image is not corrupted

4. **Docker networking issues**
   ```bash
   # Restart all services
   docker-compose down && docker-compose up --build

   # Check service health
   docker-compose ps
   ```

5. **Memory issues with large models**
   - Use lighter models like `moondream`
   - Increase Docker memory limits
   - Close other applications

### Debug Mode

Enable detailed logging:

```bash
# Backend
cd backend
PYTHONPATH=. python -c "import logging; logging.basicConfig(level=logging.DEBUG); import uvicorn; uvicorn.run('app.main:app', reload=True)"

# Test integration
python test_integration.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest backend/tests/`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Ollama** for providing local AI inference
- **FastAPI** for the excellent Python web framework
- **React** and **shadcn/ui** for the beautiful frontend
- **Lovable** for the initial frontend scaffolding

## 📞 Support

- Create an [issue](../../issues) for bug reports
- Check the [troubleshooting](#-troubleshooting) section
- Review the [API documentation](http://localhost:8000/docs) when backend is running

---

Made with ❤️ by Muaaz Bin Saeed