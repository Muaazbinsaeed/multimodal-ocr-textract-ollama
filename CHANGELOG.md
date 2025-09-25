# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-09-25

### Added

#### Complete Infrastructure & Control Scripts
- **Service Management Scripts**: start.sh, stop.sh, restart.sh for local services
- **Docker Control Script**: docker-control.sh with comprehensive Docker management
- **Test Script**: test.sh for running all available test suites
- **Enhanced Setup Script**: Better error handling and fallback package installation

#### Docker & Build Improvements
- **Fixed Docker Issues**: Updated Dockerfiles with proper dependency handling
- **Added .dockerignore Files**: Optimized Docker builds for backend and frontend
- **Fixed pyproject.toml**: Added hatchling package specification to resolve build errors
- **Updated Docker Compose**: Corrected model configuration to moondream:1.8b

#### Configuration Standardization
- **Fixed .env.example**: Updated model reference from moondream:v2 to moondream:1.8b
- **Consistent Model Names**: All configuration files now use correct model names
- **Improved Error Handling**: Better fallback mechanisms in setup processes

### Changed
- **README.md**: Comprehensive update with control scripts documentation
- **Installation Process**: Three clear options (Auto Setup, Docker, Manual)
- **Script Architecture**: All scripts are executable and follow consistent patterns
- **Error Handling**: Improved robustness in setup and installation processes

### Fixed
- **Docker Build Process**: Resolved hatchling build failures
- **npm Installation**: Added --legacy-peer-deps fallback for compatibility
- **Model Configuration**: Consistent use of moondream:1.8b across all configs
- **Script Permissions**: All scripts properly executable with chmod +x

### Technical Improvements
- **Service Management**: Proper process cleanup and port management
- **Docker Orchestration**: Complete lifecycle management (up, down, logs, status, clean)
- **Testing Framework**: Unified testing approach across shell and Python
- **Documentation**: Clear instructions for all deployment methods

## [1.1.0] - 2025-09-24

### Added

#### Enhanced Model Management
- **Model Configuration via models.txt**: Centralized model management through configuration file
- **Automatic Model Pulling**: Auto-download missing models when switching (with 10-minute timeout)
- **New /api/pull-model endpoint**: Manual model downloading with progress feedback
- **Enhanced Model Validation**: Validates against supported models list from models.txt
- **model_utils.py**: Centralized utilities for reading models configuration

#### Improved API Structure
- **Updated /api/models endpoint**: Now shows both available and supported models
- **Auto-pull support**: `/api/set-model` with configurable auto_pull parameter (default: true)
- **Better Error Handling**: Detailed error messages for model operations with timeout handling
- **Enhanced Response Structure**: Clear distinction between supported vs available models

#### Frontend Enhancements
- **Model Download Buttons**: One-click download for missing supported models
- **Real-time Progress**: Toast notifications for download/switch operations with loading states
- **Enhanced Model Selector**: Visual indicators for model states and download progress
- **Improved UX**: Better feedback, error handling, and connection status indicators
- **Auto-refresh**: Model list updates after successful operations

#### Testing & Development
- **Model Pulling Tests**: Comprehensive test coverage for new functionality (7/7 tests passing)
- **Enhanced Test Suite**: Updated API test with model management operations
- **Better Test Coverage**: Model switching, pulling, and error handling
- **Test Result Fix**: Fixed test summary reporting for accurate pass/fail counts

### Changed
- **Model Management Architecture**: Refactored to use models.txt as single source of truth
- **API Response Structure**: Enhanced with supported_models and available_models fields
- **Configuration Management**: Simplified model addition/removal through text file
- **Default Models**: Cleaned up models.txt with proper ordering (moondream:1.8b as default)

### Fixed
- **Models Configuration**: Removed duplicate moondream:latest entry from models.txt
- **Test Files**: Fixed test image paths and validation issues
- **Code Cleanup**: Removed Python cache files, unnecessary processes, and system files
- **Test Reporting**: Fixed variable name conflict in test results summary
- **Virtual Environment**: Proper backend dependency installation and activation

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