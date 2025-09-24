import { useState, useEffect } from "react";
import { Copy, CheckCircle, AlertTriangle, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useToast } from "@/hooks/use-toast";

interface ExtractionResult {
  text: string;
  model: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

interface ResultPanelProps {
  result: ExtractionResult | null;
  error: string | null;
  isProcessing: boolean;
}

export function ResultPanel({ result, error, isProcessing }: ResultPanelProps) {
  const [copied, setCopied] = useState(false);
  const [processingTime, setProcessingTime] = useState(0);
  const { toast } = useToast();

  // Timer for processing feedback
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isProcessing) {
      setProcessingTime(0);
      interval = setInterval(() => {
        setProcessingTime(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isProcessing]);

  const handleCopy = async () => {
    if (!result?.text) return;

    try {
      await navigator.clipboard.writeText(result.text);
      setCopied(true);
      toast({
        title: "Copied to clipboard",
        description: "The extracted text has been copied successfully.",
      });
      
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast({
        variant: "destructive",
        title: "Failed to copy",
        description: "Could not copy text to clipboard.",
      });
    }
  };

  if (isProcessing) {
    const formatTime = (seconds: number) => {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return mins > 0 ? `${mins}:${secs.toString().padStart(2, '0')}` : `${secs}s`;
    };

    const getProgressMessage = (time: number) => {
      if (time < 30) return "Initializing AI model...";
      if (time < 60) return "Analyzing image content...";
      if (time < 120) return "Extracting text and generating description...";
      if (time < 240) return "Processing complex image content...";
      return "Complex image detected, this may take several more minutes...";
    };

    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardContent className="p-8">
          <div className="text-center space-y-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <div>
              <h3 className="font-semibold">Processing locally via Ollama...</h3>
              <p className="text-sm text-muted-foreground mt-1">
                {getProgressMessage(processingTime)}
              </p>
              <div className="flex items-center justify-center gap-2 mt-3 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                <span>Processing time: {formatTime(processingTime)}</span>
                {processingTime > 120 && (
                  <span className="text-yellow-600 dark:text-yellow-400">
                    • Complex image detected
                  </span>
                )}
              </div>
              {processingTime > 180 && (
                <p className="text-xs text-muted-foreground mt-2">
                  Maximum processing time is 5 minutes. Please wait...
                </p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardContent className="p-6">
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="ml-2">
              <strong>Error:</strong> {error}
              {error.includes("Ollama") && (
                <div className="mt-2 text-sm">
                  <p>Make sure Ollama is running locally:</p>
                  <code className="bg-destructive/10 px-2 py-1 rounded text-xs">
                    ollama serve
                  </code>
                </div>
              )}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!result) {
    return null;
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Extracted Text</CardTitle>
          <div className="flex items-center gap-2">
            {result.usage && (
              <span className="text-xs text-muted-foreground">
                {result.usage.total_tokens} tokens
              </span>
            )}
            <span className="text-xs text-muted-foreground px-2 py-1 bg-muted rounded">
              {result.model}
            </span>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="relative">
          <Textarea
            value={result.text || "No text found in the image."}
            readOnly
            placeholder="No text extracted..."
            className="min-h-[200px] resize-none font-mono text-sm"
            aria-label="Extracted text content"
          />
        </div>
        
        {result.text && (
          <div className="flex gap-2">
            <Button
              onClick={handleCopy}
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              {copied ? (
                <>
                  <CheckCircle className="h-4 w-4 text-success" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="h-4 w-4" />
                  Copy Text
                </>
              )}
            </Button>
            
            <div className="flex-1 text-right">
              <span className="text-xs text-muted-foreground">
                {result.text.length} characters
              </span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}