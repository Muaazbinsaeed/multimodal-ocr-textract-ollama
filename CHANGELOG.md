# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-24

### Added

#### Backend Features
- **Model Management API**: Complete model switching capabilities
  - `/api/models` - List available Ollama models
  - `/api/set-model` - Switch active model dynamically
  - `/api/ollama-status` - Check Ollama connectivity status
- **Enhanced OCR Processing**: Smart OCR + Description mode
  - Flexible text extraction with intelligent descriptions
  - Extended 5-minute timeout for complex images
  - Improved error handling and user feedback
- **Configuration Management**:
  - `.env` support with example file
  - Dynamic model configuration
  - Extended request timeout (300000ms)

#### Frontend Features
- **Progressive UI Feedback**:
  - Real-time processing timer
  - Contextual status messages
  - Complex image detection warnings
  - Enhanced error handling with helpful tips
- **Model Selection** (Planned):
  - Dropdown model selector
  - Ollama status indicator
  - Real-time model switching

#### Development Tools
- **Comprehensive Testing Suite**:
  - Shell-based API tests (`tests/test_api.sh`)
  - Python test automation (`tests/api_test.py`)
  - Complete endpoint coverage
- **Master Setup Script**:
  - Automated Ollama installation and setup
  - Model management from `models.txt`
  - Process cleanup and service orchestration
  - Docker support option
- **Project Structure**:
  - Organized test samples in `tests/samples/`
  - Centralized scripts in `scripts/`
  - Clean documentation structure

#### Documentation
- **Enhanced README**: Updated with model selection, API examples
- **API Documentation**: Complete curl and Python examples
- **CHANGELOG**: Detailed version tracking
- **CLAUDE.md**: Updated development guidelines

### Changed
- **Default Model**: Changed from `llava` to `moondream:v2` for better performance
- **Request Timeout**: Increased from 180s to 300s (5 minutes)
- **Project Structure**: Reorganized for better maintainability
- **Error Messages**: More descriptive and actionable error feedback

### Technical Details
- **Backend**: FastAPI with async model switching
- **Frontend**: React with enhanced progress feedback
- **Testing**: Dual test suites (Shell + Python)
- **Setup**: Automated installation and configuration
- **Models**: Support for multiple vision models (moondream, llava, llama3.2-vision)

### API Endpoints
```
GET  /                    - Basic API information
GET  /healthz             - Health check with Ollama status
GET  /api/models          - List available models
POST /api/set-model       - Switch active model
GET  /api/ollama-status   - Detailed Ollama status
POST /api/extract-text    - OCR text extraction
```

### Supported Models
- `moondream:v2` (default) - Fast, excellent OCR + description
- `llava:latest` - Medium speed, very good accuracy
- `llama3.2-vision:latest` - Slow, excellent accuracy
- Additional models configurable via `models.txt`

### Installation
```bash
# Quick start
bash scripts/setup.sh --test

# Manual setup
cd backend && uvicorn app.main:app --reload
cd frontend && npm run dev

# Run tests
bash tests/test_api.sh
python3 tests/api_test.py
```

---

## [0.1.0] - Initial Release

### Added
- Basic OCR functionality with Ollama integration
- FastAPI backend with image upload
- React frontend with drag-and-drop
- Docker support
- Basic error handling