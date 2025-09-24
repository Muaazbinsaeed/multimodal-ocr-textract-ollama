#!/usr/bin/env python3
"""
Integration test script for the Ollama OCR application.
This script tests the backend API endpoints and provides debugging info.
"""

import requests
import time
import json
from PIL import Image
from io import BytesIO


def create_test_image_with_text():
    """Create a simple test image with text"""
    from PIL import Image, ImageDraw, ImageFont

    # Create a white background image
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)

    # Try to use default font
    try:
        # Use a basic font
        font = ImageFont.load_default()
    except:
        font = None

    # Draw some text
    text = "Hello World!\nThis is a test image.\nExtract this text."
    draw.text((20, 50), text, fill='black', font=font)

    # Save to BytesIO
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return img_bytes


def test_backend_health():
    """Test backend health endpoint"""
    print("🔍 Testing backend health...")

    try:
        response = requests.get("http://localhost:8000/healthz", timeout=10)
        print(f"✅ Backend health: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   - Ollama connected: {data.get('ollama_connected', 'unknown')}")
            print(f"   - Ollama host: {data.get('ollama_host', 'unknown')}")
            print(f"   - Ollama model: {data.get('ollama_model', 'unknown')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend at http://localhost:8000")
        print("   Make sure the backend is running: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False


def test_text_extraction():
    """Test text extraction endpoint"""
    print("\n🔍 Testing text extraction...")

    try:
        # Create test image
        test_image = create_test_image_with_text()

        # Prepare the request
        files = {'file': ('test.png', test_image, 'image/png')}

        print("   Sending request to backend...")
        response = requests.post(
            "http://localhost:8000/api/extract-text",
            files=files,
            timeout=120  # Allow longer timeout for model inference
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ Text extraction successful!")
            print(f"   - Model: {data.get('model', 'unknown')}")
            print(f"   - Extracted text: {repr(data.get('text', ''))}")

            usage = data.get('usage')
            if usage:
                print(f"   - Token usage: {usage}")

            return True

        else:
            print(f"❌ Text extraction failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Request timed out - this might mean Ollama is processing but taking a long time")
        return False
    except Exception as e:
        print(f"❌ Text extraction error: {e}")
        return False


def test_file_validation():
    """Test file validation"""
    print("\n🔍 Testing file validation...")

    # Test invalid file type
    try:
        files = {'file': ('test.txt', BytesIO(b'not an image'), 'text/plain')}
        response = requests.post("http://localhost:8000/api/extract-text", files=files)

        if response.status_code == 400:
            print("✅ File type validation working")
        else:
            print(f"⚠️  Expected 400 for invalid file type, got {response.status_code}")

    except Exception as e:
        print(f"❌ File validation test error: {e}")


def test_ollama_direct():
    """Test direct connection to Ollama"""
    print("\n🔍 Testing direct Ollama connection...")

    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is accessible")
            tags = response.json()
            models = [model['name'] for model in tags.get('models', [])]
            print(f"   Available models: {models}")

            if 'llava' in str(models).lower():
                print("✅ llava model available")
            else:
                print("⚠️  llava model not found. Install with: ollama pull llava")

        else:
            print(f"❌ Ollama responded with {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama at http://localhost:11434")
        print("   Make sure Ollama is running: ollama serve")
    except Exception as e:
        print(f"❌ Ollama connection error: {e}")


def main():
    """Run all integration tests"""
    print("🚀 Starting integration tests for Ollama OCR application\n")

    # Test Ollama direct connection first
    test_ollama_direct()

    # Test backend health
    backend_healthy = test_backend_health()

    if backend_healthy:
        # Test file validation
        test_file_validation()

        # Test text extraction
        test_text_extraction()
    else:
        print("\n❌ Skipping further tests due to backend connection issues")

    print("\n" + "="*60)
    print("🏁 Integration tests completed!")
    print("\nTo start the services:")
    print("  Backend: cd backend && uvicorn app.main:app --reload")
    print("  Frontend: cd frontend && npm run dev")
    print("  Ollama: ollama serve")
    print("  Model: ollama pull llava")


if __name__ == "__main__":
    main()