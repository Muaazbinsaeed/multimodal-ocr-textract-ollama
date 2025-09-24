import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from io import BytesIO

from app.main import app
from app.schemas import ExtractTextResponse, TokenUsage


client = TestClient(app)


def create_test_image() -> BytesIO:
    """Create a simple test image"""
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='white')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


class TestExtractText:

    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Ollama OCR API"

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        with patch('app.ollama_client.ollama_client.health_check') as mock_health:
            mock_health.return_value = True
            response = client.get("/healthz")
            assert response.status_code == 200
            data = response.json()
            assert data["ollama_connected"] is True

    def test_extract_text_no_file(self):
        """Test extract text endpoint without file"""
        response = client.post("/api/extract-text")
        assert response.status_code == 422  # Validation error

    def test_extract_text_invalid_file_type(self):
        """Test extract text with invalid file type"""
        # Create a text file instead of image
        text_content = b"This is not an image"
        response = client.post(
            "/api/extract-text",
            files={"file": ("test.txt", BytesIO(text_content), "text/plain")}
        )
        assert response.status_code == 400

    def test_extract_text_oversized_file(self):
        """Test extract text with oversized file"""
        # Create a large fake image (simulate > 10MB)
        large_content = b"0" * (11 * 1024 * 1024)  # 11MB of zeros
        response = client.post(
            "/api/extract-text",
            files={"file": ("large.png", BytesIO(large_content), "image/png")}
        )
        assert response.status_code == 400

    @patch('app.ollama_client.ollama_client.extract_text_from_image')
    @patch('app.image_utils.validate_and_encode_image')
    def test_extract_text_success(self, mock_validate, mock_extract):
        """Test successful text extraction"""
        # Mock the validation and encoding
        mock_validate.return_value = ("base64_image_data", "image/png")

        # Mock the Ollama response
        mock_result = ExtractTextResponse(
            text="Sample extracted text",
            model="llava",
            usage=TokenUsage(
                prompt_tokens=10,
                completion_tokens=20,
                total_tokens=30
            )
        )
        mock_extract.return_value = mock_result

        # Create test image
        test_image = create_test_image()

        response = client.post(
            "/api/extract-text",
            files={"file": ("test.png", test_image, "image/png")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Sample extracted text"
        assert data["model"] == "llava"
        assert data["usage"]["total_tokens"] == 30

    @patch('app.ollama_client.ollama_client.extract_text_from_image')
    @patch('app.image_utils.validate_and_encode_image')
    def test_extract_text_ollama_error(self, mock_validate, mock_extract):
        """Test Ollama service error"""
        from app.errors import OllamaConnectionError

        # Mock the validation
        mock_validate.return_value = ("base64_image_data", "image/png")

        # Mock Ollama error
        mock_extract.side_effect = OllamaConnectionError()

        # Create test image
        test_image = create_test_image()

        response = client.post(
            "/api/extract-text",
            files={"file": ("test.png", test_image, "image/png")}
        )

        assert response.status_code == 503
        data = response.json()
        assert "error" in data
        assert data["code"] == 503


if __name__ == "__main__":
    pytest.main([__file__])