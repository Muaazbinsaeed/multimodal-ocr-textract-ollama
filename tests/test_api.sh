#!/bin/bash

# Multimodal OCR API Test Suite
# Tests all API endpoints with curl commands

echo "🚀 Starting API Test Suite"
echo "=================================="

BASE_URL="http://localhost:8000"
SAMPLE_IMAGE="tests/samples/sample_emirates_id.jpg"

# Check if backend is running
echo "1. Testing backend connectivity..."
response=$(curl -s -o /dev/null -w "%{http_code}" ${BASE_URL}/)
if [ $response -eq 200 ]; then
    echo "✅ Backend is running"
else
    echo "❌ Backend not accessible (HTTP $response)"
    echo "Start with: cd backend && uvicorn app.main:app --reload"
    exit 1
fi

# Test health endpoint
echo -e "\n2. Testing health endpoint..."
curl -s ${BASE_URL}/healthz | python3 -m json.tool

# Test Ollama status
echo -e "\n3. Testing Ollama status..."
curl -s ${BASE_URL}/api/ollama-status | python3 -m json.tool

# Test models endpoint
echo -e "\n4. Testing available models..."
curl -s ${BASE_URL}/api/models | python3 -m json.tool

# Test model switching
echo -e "\n5. Testing model switching..."
current_model=$(curl -s ${BASE_URL}/api/models | python3 -c "import sys, json; print(json.load(sys.stdin)['current_model'])")
echo "Current model: $current_model"

# Try to switch to moondream:1.8b if different
if [ "$current_model" != "moondream:1.8b" ]; then
    echo "Switching to moondream:1.8b..."
    curl -s -X POST ${BASE_URL}/api/set-model \
        -H "Content-Type: application/json" \
        -d '{"model": "moondream:1.8b"}' | python3 -m json.tool
fi

# Test OCR endpoint
echo -e "\n6. Testing OCR text extraction..."
if [ -f "$SAMPLE_IMAGE" ]; then
    echo "Using sample image: $SAMPLE_IMAGE"
    curl -s -X POST ${BASE_URL}/api/extract-text \
        -F "file=@${SAMPLE_IMAGE}" | python3 -m json.tool
else
    echo "⚠️  Sample image not found: $SAMPLE_IMAGE"
    echo "Skipping OCR test"
fi

echo -e "\n=================================="
echo "🏁 API Test Suite Completed"

# Example curl commands for manual testing
echo -e "\n📖 Manual Test Commands:"
echo "# Health check:"
echo "curl -s ${BASE_URL}/healthz | python3 -m json.tool"
echo ""
echo "# Get available models:"
echo "curl -s ${BASE_URL}/api/models | python3 -m json.tool"
echo ""
echo "# Switch model:"
echo "curl -s -X POST ${BASE_URL}/api/set-model -H 'Content-Type: application/json' -d '{\"model\": \"moondream:v2\"}' | python3 -m json.tool"
echo ""
echo "# OCR extraction:"
echo "curl -s -X POST ${BASE_URL}/api/extract-text -F 'file=@path/to/image.jpg' | python3 -m json.tool"