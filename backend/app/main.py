from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from .config import settings
from .schemas import ExtractTextResponse, ErrorResponse
from .errors import (
    OllamaError,
    ImageValidationError,
    create_error_response
)
from .image_utils import validate_and_encode_image
from .ollama_client import ollama_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Ollama OCR API",
    description="Extract text from images using Ollama multimodal models",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "Ollama OCR API",
        "version": "1.0.0",
        "model": settings.ollama_model,
        "max_file_size_mb": settings.max_upload_mb
    }


@app.get("/healthz")
async def health_check():
    """Health check endpoint that also verifies Ollama connectivity"""
    ollama_status = await ollama_client.health_check()

    return {
        "status": "healthy" if ollama_status else "degraded",
        "ollama_connected": ollama_status,
        "ollama_host": settings.ollama_host,
        "ollama_model": settings.ollama_model
    }


@app.post("/api/extract-text", response_model=ExtractTextResponse)
async def extract_text(file: UploadFile = File(...)):
    """
    Extract text from uploaded image using Ollama multimodal models

    - **file**: Image file (PNG, JPEG, WebP, max 10MB)

    Returns the extracted text along with model information and token usage.
    """
    try:
        # Log request
        logger.info(f"Processing text extraction for file: {file.filename}")

        # Validate and encode image
        base64_image, mime_type = await validate_and_encode_image(file)

        # Extract text using Ollama
        result = await ollama_client.extract_text_from_image(base64_image)

        # Log successful extraction
        logger.info(f"Successfully extracted text from {file.filename} using {result.model}")

        return result

    except ImageValidationError as e:
        logger.warning(f"Image validation failed for {file.filename}: {str(e)}")
        raise e

    except OllamaError as e:
        logger.error(f"Ollama error for {file.filename}: {str(e)}")
        error_response = create_error_response(e)
        return JSONResponse(
            status_code=e.status_code,
            content=error_response
        )

    except Exception as e:
        logger.error(f"Unexpected error processing {file.filename}: {str(e)}")
        error_response = create_error_response(e)
        return JSONResponse(
            status_code=500,
            content=error_response
        )


@app.get("/api/models")
async def get_available_models():
    """Get list of available Ollama models"""
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{settings.ollama_host}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                # Filter for multimodal models (those that can handle images)
                vision_models = [m for m in models if any(keyword in m.lower() for keyword in ['llava', 'moondream', 'vision', 'bakllava', 'qwen2-vl', 'minicpm-v'])]

                return {
                    "available_models": vision_models,
                    "current_model": settings.ollama_model,
                    "all_models": models
                }
            else:
                raise HTTPException(status_code=503, detail="Cannot connect to Ollama")

    except Exception as e:
        logger.error(f"Error fetching models: {str(e)}")
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama")


@app.post("/api/set-model")
async def set_model(model_data: dict):
    """Set the active Ollama model"""
    model_name = model_data.get('model')
    if not model_name:
        raise HTTPException(status_code=400, detail="Model name required")

    try:
        # Validate model exists in Ollama
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{settings.ollama_host}/api/tags")
            if response.status_code == 200:
                data = response.json()
                available_models = [model['name'] for model in data.get('models', [])]

                if model_name not in available_models:
                    raise HTTPException(status_code=400, detail=f"Model '{model_name}' not found in Ollama")

                # Update the current model (in memory)
                settings.ollama_model = model_name
                ollama_client.model = model_name

                logger.info(f"Switched to model: {model_name}")

                return {
                    "message": f"Successfully switched to model: {model_name}",
                    "current_model": model_name
                }
            else:
                raise HTTPException(status_code=503, detail="Cannot connect to Ollama")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting model: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/ollama-status")
async def get_ollama_status():
    """Check Ollama connectivity and status"""
    try:
        is_connected = await ollama_client.health_check()

        if is_connected:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.ollama_host}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    model_count = len(data.get('models', []))

                    return {
                        "status": "connected",
                        "host": settings.ollama_host,
                        "current_model": settings.ollama_model,
                        "total_models": model_count
                    }

        return {
            "status": "disconnected",
            "host": settings.ollama_host,
            "error": "Cannot connect to Ollama"
        }

    except Exception as e:
        logger.error(f"Error checking Ollama status: {str(e)}")
        return {
            "status": "error",
            "host": settings.ollama_host,
            "error": str(e)
        }


@app.exception_handler(ImageValidationError)
async def validation_exception_handler(request, exc: ImageValidationError):
    """Handle image validation errors"""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc)
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc)
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )