import httpx
import asyncio
import re
from typing import Optional, Dict, Any
from urllib.parse import urljoin

from .config import settings
from .schemas import ExtractTextResponse, TokenUsage
from .errors import OllamaConnectionError, OllamaTimeoutError, OllamaModelError


class OllamaClient:
    def __init__(self):
        self.base_url = settings.ollama_host
        self.model = settings.ollama_model
        self.timeout = settings.request_timeout_seconds

        # System instruction for flexible text extraction and image analysis
        self.system_prompt = (
            "You are a helpful AI assistant that can read text from images and describe what you see. "
            "When analyzing images, please:\n"
            "1. Extract all visible text exactly as it appears\n"
            "2. Preserve formatting, line breaks, and spacing when possible\n"
            "3. Provide a brief description of what the image contains\n"
            "4. If it's an ID card, document, or form, identify the type and key information\n"
            "Be comprehensive but concise in your response."
        )

    async def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to Ollama with error handling and retries"""
        url = urljoin(self.base_url, endpoint)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)

                if response.status_code == 404:
                    if "model" in response.text.lower():
                        raise OllamaModelError(self.model)
                    else:
                        # Endpoint not found, will be used for fallback logic
                        raise httpx.HTTPStatusError(
                            f"HTTP {response.status_code}",
                            request=response.request,
                            response=response
                        )

                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                raise OllamaTimeoutError()
            except httpx.ConnectError:
                raise OllamaConnectionError()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise
                # Re-raise for other HTTP errors
                raise OllamaConnectionError(
                    f"Ollama returned HTTP {e.response.status_code}: {e.response.text}"
                )

    async def _extract_with_chat_api(self, base64_image: str) -> Dict[str, Any]:
        """Try extraction using /api/chat endpoint"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": "Please analyze this image. Extract any text you can see and describe what the image contains.",
                    "images": [base64_image]
                }
            ],
            "stream": False
        }

        response = await self._make_request("/api/chat", payload)
        return response

    async def _extract_with_generate_api(self, base64_image: str) -> Dict[str, Any]:
        """Fallback extraction using /api/generate endpoint"""
        payload = {
            "model": self.model,
            "prompt": "Please analyze this image. Extract any text you can see and describe what the image contains.",
            "images": [base64_image],
            "stream": False
        }

        response = await self._make_request("/api/generate", payload)
        return response

    def _clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""

        # Remove common prefixes/suffixes that models might add
        text = text.strip()

        # Remove code fence markers if present
        text = re.sub(r'^```[\w]*\n?', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n?```$', '', text, flags=re.MULTILINE)

        # Only remove truly redundant prefixes that don't add value
        redundant_prefixes = [
            "Here is the text from the image:",
            "The text in the image is:",
            "Text extracted from image:",
            "The extracted text is:"
        ]

        for prefix in redundant_prefixes:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()

        return text.strip()

    def _parse_response(self, response: Dict[str, Any], api_type: str) -> ExtractTextResponse:
        """Parse Ollama response and extract text and usage info"""
        if api_type == "chat":
            # Parse /api/chat response
            message = response.get("message", {})
            raw_text = message.get("content", "")
            usage_data = response.get("usage", {})
        else:
            # Parse /api/generate response
            raw_text = response.get("response", "")
            usage_data = response.get("usage", {})

        # Clean the extracted text
        cleaned_text = self._clean_extracted_text(raw_text)

        # Parse usage information if available
        usage = None
        if usage_data:
            usage = TokenUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0)
            )

        return ExtractTextResponse(
            text=cleaned_text,
            model=self.model,
            usage=usage
        )

    async def extract_text_from_image(self, base64_image: str) -> ExtractTextResponse:
        """
        Extract text from base64-encoded image using Ollama multimodal models.
        Tries /api/chat first, falls back to /api/generate if needed.
        """
        try:
            # Try /api/chat first (preferred)
            response = await self._extract_with_chat_api(base64_image)
            return self._parse_response(response, "chat")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Fallback to /api/generate
                try:
                    response = await self._extract_with_generate_api(base64_image)
                    return self._parse_response(response, "generate")
                except Exception:
                    # Re-raise original chat API error
                    raise OllamaConnectionError(
                        f"Both /api/chat and /api/generate endpoints failed. "
                        f"Make sure Ollama is running and the model '{self.model}' is available."
                    )
            else:
                raise

    async def health_check(self) -> bool:
        """Check if Ollama is accessible"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(urljoin(self.base_url, "/api/tags"))
                return response.status_code == 200
        except Exception:
            return False


# Global client instance
ollama_client = OllamaClient()