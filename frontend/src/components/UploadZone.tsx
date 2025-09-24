import { useState, useCallback } from "react";
import { Upload, FileImage, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface FilePreview {
  file: File;
  preview: string;
}

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  isProcessing: boolean;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/webp'];

export function UploadZone({ onFileSelect, isProcessing }: UploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [filePreview, setFilePreview] = useState<FilePreview | null>(null);
  const [error, setError] = useState<string | null>(null);

  const validateFile = (file: File): string | null => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return "Please upload a PNG, JPEG, or WebP image.";
    }
    if (file.size > MAX_FILE_SIZE) {
      return "File size must be less than 10MB.";
    }
    return null;
  };

  const handleFile = useCallback((file: File) => {
    setError(null);
    
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      setFilePreview({
        file,
        preview: e.target?.result as string
      });
    };
    reader.readAsDataURL(file);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  }, [handleFile]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  }, [handleFile]);

  const handleExtractText = () => {
    if (filePreview) {
      onFileSelect(filePreview.file);
    }
  };

  const resetUpload = () => {
    setFilePreview(null);
    setError(null);
  };

  return (
    <div className="w-full max-w-md mx-auto space-y-4">
      {!filePreview ? (
        <Card
          className={`relative border-2 border-dashed transition-all duration-200 ${
            isDragOver
              ? "border-primary bg-upload-active"
              : "border-upload-border bg-upload hover:bg-upload-hover"
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="p-8 text-center">
            <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Upload an image</h3>
            <p className="text-muted-foreground text-sm mb-4">
              Drag and drop an image here, or click to browse
            </p>
            <p className="text-xs text-muted-foreground mb-4">
              PNG, JPEG, WebP up to 10MB
            </p>
            
            <input
              type="file"
              accept=".png,.jpg,.jpeg,.webp"
              onChange={handleFileInput}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              aria-label="Upload image file"
            />
            
            <Button variant="outline" className="pointer-events-none">
              Choose Image
            </Button>
          </div>
        </Card>
      ) : (
        <Card className="p-4">
          <div className="flex items-start gap-4">
            <div className="relative flex-shrink-0">
              <img
                src={filePreview.preview}
                alt="Uploaded preview"
                className="w-16 h-16 object-cover rounded-lg border"
              />
              <FileImage className="absolute -top-1 -right-1 h-4 w-4 text-primary bg-background rounded-full p-0.5" />
            </div>
            
            <div className="flex-1 min-w-0">
              <p className="font-medium text-sm truncate">{filePreview.file.name}</p>
              <p className="text-xs text-muted-foreground">
                {(filePreview.file.size / 1024 / 1024).toFixed(1)} MB
              </p>
            </div>
          </div>
          
          <div className="flex gap-2 mt-4">
            <Button 
              onClick={handleExtractText} 
              disabled={isProcessing}
              className="flex-1"
            >
              {isProcessing ? "Processing..." : "Extract Text"}
            </Button>
            <Button variant="outline" onClick={resetUpload} disabled={isProcessing}>
              Change
            </Button>
          </div>
        </Card>
      )}

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  );
}