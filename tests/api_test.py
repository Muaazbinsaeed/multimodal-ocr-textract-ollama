#!/usr/bin/env python3
"""
Comprehensive API Test Suite for Multimodal OCR
Tests all backend endpoints with Python requests
"""

import requests
import os
import json
import time
from pathlib import Path


class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_image = "tests/samples/sample_emirates_id.jpg"

    def test_connectivity(self):
        """Test basic backend connectivity"""
        print("🔍 Testing backend connectivity...")
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ Backend is running")
                data = response.json()
                print(f"   Version: {data.get('version', 'unknown')}")
                print(f"   Model: {data.get('model', 'unknown')}")
                return True
            else:
                print(f"❌ Backend returned {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to backend")
            print("   Start with: cd backend && uvicorn app.main:app --reload")
            return False

    def test_health_check(self):
        """Test health endpoint"""
        print("\n🔍 Testing health endpoint...")
        try:
            response = requests.get(f"{self.base_url}/healthz", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("✅ Health check passed")
                print(f"   Ollama connected: {data.get('ollama_connected', 'unknown')}")
                print(f"   Ollama host: {data.get('ollama_host', 'unknown')}")
                print(f"   Model: {data.get('ollama_model', 'unknown')}")
                return data.get('ollama_connected', False)
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

    def test_ollama_status(self):
        """Test Ollama status endpoint"""
        print("\n🔍 Testing Ollama status...")
        try:
            response = requests.get(f"{self.base_url}/api/ollama-status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Ollama status: {data.get('status', 'unknown')}")
                print(f"   Host: {data.get('host', 'unknown')}")
                print(f"   Current model: {data.get('current_model', 'unknown')}")
                print(f"   Total models: {data.get('total_models', 'unknown')}")
                return data.get('status') == 'connected'
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Status check error: {e}")
            return False

    def test_models_endpoint(self):
        """Test models listing endpoint"""
        print("\n🔍 Testing models endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("✅ Models endpoint working")
                print(f"   Available models: {len(data.get('available_models', []))}")
                print(f"   Supported models: {len(data.get('supported_models', []))}")
                print(f"   Current model: {data.get('current_model', 'unknown')}")
                print(f"   Available: {data.get('available_models', [])}")
                print(f"   Supported: {data.get('supported_models', [])}")
                return data
            else:
                print(f"❌ Models endpoint failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Models endpoint error: {e}")
            return None

    def test_model_switching(self, target_model="moondream:1.8b"):
        """Test model switching"""
        print(f"\n🔍 Testing model switching to {target_model}...")
        try:
            # First, check available models
            models_data = self.test_models_endpoint()
            if not models_data:
                return False

            available_models = models_data.get('available_models', [])
            current_model = models_data.get('current_model', '')

            if target_model not in available_models:
                print(f"⚠️  Target model '{target_model}' not available")
                print(f"   Available models: {available_models}")
                return False

            if current_model == target_model:
                print(f"✅ Already using {target_model}")
                return True

            # Switch model
            response = requests.post(
                f"{self.base_url}/api/set-model",
                json={"model": target_model},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Successfully switched to {target_model}")
                print(f"   Message: {data.get('message', 'Success')}")
                return True
            else:
                print(f"❌ Model switching failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Model switching error: {e}")
            return False

    def test_model_pulling(self):
        """Test model pulling functionality"""
        print(f"\n🔍 Testing model pulling...")

        # Get models data first
        models_data = self.test_models_endpoint()
        if not models_data:
            print("⚠️  Cannot test model pulling without models data")
            return False

        supported_models = models_data.get('supported_models', [])
        available_models = models_data.get('available_models', [])

        # Find a model that's supported but not available (for testing pull)
        missing_models = [m for m in supported_models if m not in available_models]

        if not missing_models:
            print("✅ All supported models are already available")
            return True

        # Test pulling the first missing model (with a quick timeout for testing)
        test_model = missing_models[0]
        print(f"   Testing pull for: {test_model}")

        try:
            # Test the pull endpoint (but we'll use a short timeout for testing)
            response = requests.post(
                f"{self.base_url}/api/pull-model",
                json={"model": test_model},
                timeout=30  # Short timeout for testing
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Model pull initiated: {data.get('message', 'Success')}")
                return True
            elif response.status_code == 408:  # Timeout expected for large models
                print(f"✅ Model pull started (timed out as expected)")
                return True
            else:
                print(f"❌ Model pull failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text}")
                return False

        except requests.exceptions.Timeout:
            print("✅ Model pull started (timed out as expected)")
            return True
        except Exception as e:
            print(f"❌ Model pulling error: {e}")
            return False

    def test_ocr_extraction(self):
        """Test OCR text extraction"""
        print(f"\n🔍 Testing OCR extraction...")

        if not os.path.exists(self.test_image):
            print(f"⚠️  Test image not found: {self.test_image}")
            return False

        try:
            with open(self.test_image, 'rb') as f:
                files = {'file': (self.test_image, f, 'image/png')}

                print(f"   Uploading: {self.test_image}")
                response = requests.post(
                    f"{self.base_url}/api/extract-text",
                    files=files,
                    timeout=120  # 2-minute timeout for OCR
                )

            if response.status_code == 200:
                data = response.json()
                print("✅ OCR extraction successful")
                print(f"   Model used: {data.get('model', 'unknown')}")
                print(f"   Text length: {len(data.get('text', ''))}")
                print(f"   Extracted text: {repr(data.get('text', '')[:100])}{'...' if len(data.get('text', '')) > 100 else ''}")

                usage = data.get('usage')
                if usage:
                    print(f"   Token usage: {usage}")

                return True
            else:
                print(f"❌ OCR extraction failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Response: {response.text}")
                return False

        except requests.exceptions.Timeout:
            print("❌ OCR request timed out (>2 minutes)")
            return False
        except Exception as e:
            print(f"❌ OCR extraction error: {e}")
            return False

    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Comprehensive API Test Suite")
        print("=" * 50)

        results = {
            'connectivity': False,
            'health': False,
            'ollama_status': False,
            'models': False,
            'model_switching': False,
            'model_pulling': False,
            'ocr': False
        }

        # Test 1: Connectivity
        results['connectivity'] = self.test_connectivity()
        if not results['connectivity']:
            print("\n❌ Basic connectivity failed - stopping tests")
            return results

        # Test 2: Health check
        results['health'] = self.test_health_check()

        # Test 3: Ollama status
        results['ollama_status'] = self.test_ollama_status()

        # Test 4: Models endpoint
        models_data = self.test_models_endpoint()
        results['models'] = models_data is not None

        # Test 5: Model switching
        if models_data and results['ollama_status']:
            results['model_switching'] = self.test_model_switching()

        # Test 6: Model pulling
        if results['ollama_status']:
            results['model_pulling'] = self.test_model_pulling()

        # Test 7: OCR extraction
        if results['ollama_status']:
            results['ocr'] = self.test_ocr_extraction()

        # Summary
        print("\n" + "=" * 50)
        print("🏁 Test Suite Summary")
        print("-" * 30)

        passed = sum(results.values())
        total = len(results)

        for test_name, test_passed in results.items():
            status = "✅ PASS" if test_passed else "❌ FAIL"
            print(f"{test_name:15} {status}")

        print(f"\nResults: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! System ready for production.")
        else:
            print("⚠️  Some tests failed. Check configuration and services.")

        return results


def main():
    """Main test runner"""
    tester = APITester()
    results = tester.run_all_tests()

    # Exit with error code if any tests failed
    exit_code = 0 if all(results.values()) else 1
    exit(exit_code)


if __name__ == "__main__":
    main()