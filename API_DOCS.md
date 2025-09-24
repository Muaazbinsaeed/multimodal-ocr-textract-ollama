# API Documentation

Complete API reference for the Multimodal OCR application.

**Base URL**: `http://localhost:8000`

## Endpoints

### 1. Basic Information

#### `GET /`
Get basic API information.

**Response**:
```json
{
  "message": "Ollama OCR API",
  "version": "1.0.0",
  "model": "moondream:v2",
  "max_file_size_mb": 10
}
```

**Curl Example**:
```bash
curl -s http://localhost:8000/ | python3 -m json.tool
```

---

### 2. Health Check

#### `GET /healthz`
Check API and Ollama connectivity status.

**Response**:
```json
{
  "status": "healthy",
  "ollama_connected": true,
  "ollama_host": "http://localhost:11434",
  "ollama_model": "moondream:v2"
}
```

**Curl Example**:
```bash
curl -s http://localhost:8000/healthz | python3 -m json.tool
```

**Python Example**:
```python
import requests

response = requests.get("http://localhost:8000/healthz")
data = response.json()
print(f"Ollama connected: {data['ollama_connected']}")
```

---

### 3. Model Management

#### `GET /api/models`
List available Ollama models.

**Response**:
```json
{
  "available_models": ["moondream:1.8b"],
  "supported_models": ["moondream:1.8b", "llava:latest", "llama3.2-vision:latest"],
  "current_model": "moondream:1.8b",
  "all_models": ["moondream:1.8b", "qwen2:1.5b", "nomic-embed-text:latest"]
}
```

**Curl Example**:
```bash
curl -s http://localhost:8000/api/models | python3 -m json.tool
```

**Python Example**:
```python
import requests

response = requests.get("http://localhost:8000/api/models")
data = response.json()
print(f"Available vision models: {data['available_models']}")
print(f"Current model: {data['current_model']}")
```

#### `POST /api/set-model`
Switch the active Ollama model.

**Request Body**:
```json
{
  "model": "llava:latest",
  "auto_pull": true
}
```

**Response**:
```json
{
  "message": "Successfully switched to model: llava:latest",
  "current_model": "llava:latest"
}
```

**Curl Example**:
```bash
curl -s -X POST http://localhost:8000/api/set-model \
  -H "Content-Type: application/json" \
  -d '{"model": "llava:latest"}' | python3 -m json.tool
```

**Python Example**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/set-model",
    json={"model": "llava:latest"}
)
print(response.json())
```

#### `GET /api/ollama-status`
Get detailed Ollama status information.

**Response**:
```json
{
  "status": "connected",
  "host": "http://localhost:11434",
  "current_model": "moondream:v2",
  "total_models": 5
}
```

**Curl Example**:
```bash
curl -s http://localhost:8000/api/ollama-status | python3 -m json.tool
```

#### `POST /api/pull-model`
Download a model from Ollama registry.

**Request Body**:
```json
{
  "model": "llava:latest"
}
```

**Response**:
```json
{
  "message": "Successfully pulled model: llava:latest",
  "model": "llava:latest",
  "output": "pulling manifest\npulling 8934d96d3226... 100%\n..."
}
```

**Curl Example**:
```bash
curl -s -X POST http://localhost:8000/api/pull-model \
  -H "Content-Type: application/json" \
  -d '{"model": "llava:latest"}' | python3 -m json.tool
```

**Python Example**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/pull-model",
    json={"model": "llava:latest"},
    timeout=600  # 10-minute timeout for large models
)
print(response.json())
```

---

### 4. OCR Text Extraction

#### `POST /api/extract-text`
Extract text from an uploaded image.

**Request**: Multipart form data with image file.

**Parameters**:
- `file`: Image file (PNG, JPEG, WebP, max 10MB)

**Response**:
```json
{
  "text": "Extracted text content with description...",
  "model": "moondream:v2",
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 75,
    "total_tokens": 225
  }
}
```

**Curl Example**:
```bash
curl -s -X POST http://localhost:8000/api/extract-text \
  -F "file=@/path/to/image.jpg" | python3 -m json.tool
```

**Python Example**:
```python
import requests

with open("/path/to/image.jpg", "rb") as f:
    files = {"file": ("image.jpg", f, "image/jpeg")}
    response = requests.post(
        "http://localhost:8000/api/extract-text",
        files=files,
        timeout=300  # 5-minute timeout for complex images
    )

if response.status_code == 200:
    data = response.json()
    print(f"Model: {data['model']}")
    print(f"Text: {data['text']}")
    if data.get('usage'):
        print(f"Tokens used: {data['usage']['total_tokens']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

---

## Error Handling

### Common Error Codes

#### 400 Bad Request
- Invalid file format
- File too large (>10MB)
- Missing required parameters

```json
{
  "detail": "Invalid file format. Please upload PNG, JPEG, or WebP images."
}
```

#### 503 Service Unavailable
- Ollama service not running
- Cannot connect to Ollama

```json
{
  "detail": "Cannot connect to Ollama"
}
```

#### 504 Gateway Timeout
- Processing took longer than 5 minutes
- Complex image or server overload

```json
{
  "detail": "Request timed out. The image processing is taking too long."
}
```

---

## Complete Python Client Example

```python
#!/usr/bin/env python3
"""
Complete example of using the Multimodal OCR API
"""

import requests
import json
from pathlib import Path


class OCRClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def health_check(self):
        """Check API health"""
        response = requests.get(f"{self.base_url}/healthz")
        return response.json()

    def list_models(self):
        """Get available models"""
        response = requests.get(f"{self.base_url}/api/models")
        return response.json()

    def switch_model(self, model_name):
        """Switch to a different model"""
        response = requests.post(
            f"{self.base_url}/api/set-model",
            json={"model": model_name}
        )
        return response.json()

    def extract_text(self, image_path):
        """Extract text from image"""
        with open(image_path, "rb") as f:
            files = {"file": (Path(image_path).name, f, "image/jpeg")}
            response = requests.post(
                f"{self.base_url}/api/extract-text",
                files=files,
                timeout=300
            )

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


# Usage example
if __name__ == "__main__":
    client = OCRClient()

    # Check health
    health = client.health_check()
    print(f"Service healthy: {health['status'] == 'healthy'}")

    # List models
    models = client.list_models()
    print(f"Available models: {models['available_models']}")

    # Extract text
    result = client.extract_text("tests/samples/uae_id_card.png")
    print(f"Extracted text: {result['text']}")
```

---

## Rate Limiting

- **No rate limiting** currently implemented
- **Timeout**: 5 minutes per request for OCR processing
- **File size**: Maximum 10MB per image
- **Concurrent requests**: Limited by server resources

---

## Best Practices

1. **File Preparation**:
   - Use high-quality images for better OCR results
   - Supported formats: PNG, JPEG, WebP
   - Keep files under 10MB

2. **Error Handling**:
   - Always check response status codes
   - Implement retry logic for network issues
   - Handle timeouts gracefully (5+ minute processing)

3. **Model Selection**:
   - Use `moondream:v2` for speed and good accuracy
   - Use `llava:latest` for better accuracy
   - Switch models based on image complexity

4. **Performance**:
   - Allow 5+ minutes for complex document processing
   - Monitor token usage for cost optimization
   - Cache results when possible

---

## Testing

Run the test suites to verify API functionality:

```bash
# Shell test suite
bash tests/test_api.sh

# Python test suite
python3 tests/api_test.py
```