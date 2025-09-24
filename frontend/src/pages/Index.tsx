import { useState } from "react";
import { UploadZone } from "@/components/UploadZone";
import { ResultPanel } from "@/components/ResultPanel";
import { Header } from "@/components/Header";

interface ExtractionResult {
  text: string;
  model: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

const Index = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (file: File) => {
    setIsProcessing(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Extended timeout for complex image processing (6 minutes to match backend)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 360000); // 6 minutes

      const response = await fetch('http://localhost:8000/api/extract-text', {
        method: 'POST',
        body: formData,
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.message ||
          `Failed to extract text (${response.status})`
        );
      }

      const result: ExtractionResult = await response.json();
      setResult(result);
    } catch (err) {
      let errorMessage = "Failed to extract text. Please try again.";

      if (err instanceof Error) {
        errorMessage = err.message;
      }

      // Add helpful context for common errors
      if (errorMessage.includes("Failed to fetch") || errorMessage.includes("NetworkError")) {
        errorMessage = "Cannot connect to backend server. Please ensure the backend is running at http://localhost:8000";
      } else if (errorMessage.includes("503")) {
        errorMessage = "Ollama service is not available. Please ensure Ollama is running at http://localhost:11434 and the model (moondream:1.8b) is installed.";
      } else if (errorMessage.includes("504") || errorMessage.includes("timeout")) {
        errorMessage = "Processing timed out. This can happen with very complex images or heavy server load. Please try again or use a simpler image.";
      } else if (errorMessage.includes("abort")) {
        errorMessage = "Request was cancelled due to timeout (6 minutes exceeded). The image may be too complex for processing.";
      } else if (errorMessage.includes("413")) {
        errorMessage = "Image file is too large. Please use an image smaller than 10MB.";
      } else if (errorMessage.includes("400")) {
        errorMessage = "Invalid file format. Please upload a PNG, JPEG, or WebP image.";
      }

      setError(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="py-8 px-4">
        <div className="container max-w-4xl mx-auto space-y-8">
          {/* Main Content */}
          <div className="text-center space-y-4">
            <div>
              <h2 className="text-3xl font-bold tracking-tight">Extract Text from Images</h2>
              <p className="text-muted-foreground mt-2">
                Upload an image and extract readable text using local Ollama multimodal models
              </p>
            </div>
          </div>

          {/* Upload Zone */}
          <UploadZone onFileSelect={handleFileSelect} isProcessing={isProcessing} />

          {/* Results */}
          <ResultPanel result={result} error={error} isProcessing={isProcessing} />

          {/* Footer */}
          <div className="text-center text-xs text-muted-foreground border-t pt-6">
            <p>
              Made by: Muaaz Bin Saeed
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;