import { useState, useEffect } from "react";
import { Cpu, CheckCircle, XCircle, AlertCircle, Download } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

interface ModelData {
  available_models: string[];
  supported_models: string[];
  current_model: string;
  all_models: string[];
}

interface OllamaStatus {
  status: string;
  host: string;
  current_model: string;
  total_models: number;
}

export function ModelSelector() {
  const [modelData, setModelData] = useState<ModelData | null>(null);
  const [ollamaStatus, setOllamaStatus] = useState<OllamaStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSwitching, setIsSwitching] = useState(false);
  const [isPulling, setIsPulling] = useState(false);
  const [pullingModel, setPullingModel] = useState<string | null>(null);
  const { toast } = useToast();

  const fetchModelData = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/models");
      if (response.ok) {
        const data = await response.json();
        setModelData(data);
      }
    } catch (error) {
      console.error("Failed to fetch models:", error);
    }
  };

  const fetchOllamaStatus = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/ollama-status");
      if (response.ok) {
        const data = await response.json();
        setOllamaStatus(data);
      }
    } catch (error) {
      console.error("Failed to fetch Ollama status:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleModelChange = async (modelName: string) => {
    if (!modelData || modelName === modelData.current_model) return;

    setIsSwitching(true);
    try {
      const response = await fetch("http://localhost:8000/api/set-model", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ model: modelName }),
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: "Model Switched",
          description: `Successfully switched to ${modelName}`,
        });

        // Refresh model data
        await fetchModelData();
        await fetchOllamaStatus();
      } else {
        const errorData = await response.json();
        toast({
          title: "Error",
          description: errorData.message || "Failed to switch model",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to switch model. Check your connection.",
        variant: "destructive",
      });
    } finally {
      setIsSwitching(false);
    }
  };

  const handleModelPull = async (modelName: string) => {
    setIsPulling(true);
    setPullingModel(modelName);

    try {
      const response = await fetch("http://localhost:8000/api/pull-model", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ model: modelName }),
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: "Model Downloaded",
          description: `Successfully downloaded ${modelName}`,
        });

        // Refresh model data after pulling
        await fetchModelData();
        await fetchOllamaStatus();
      } else {
        const errorData = await response.json();
        toast({
          title: "Download Failed",
          description: errorData.detail || "Failed to download model",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to download model. Check your connection.",
        variant: "destructive",
      });
    } finally {
      setIsPulling(false);
      setPullingModel(null);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      await Promise.all([fetchModelData(), fetchOllamaStatus()]);
    };

    fetchData();

    // Refresh every 30 seconds
    const interval = setInterval(fetchOllamaStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = () => {
    if (isLoading) {
      return <AlertCircle className="h-4 w-4 text-yellow-500" />;
    }

    if (ollamaStatus?.status === "connected") {
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    }

    return <XCircle className="h-4 w-4 text-red-500" />;
  };

  const getStatusText = () => {
    if (isLoading) return "Checking...";
    if (ollamaStatus?.status === "connected") return "Connected";
    return "Disconnected";
  };

  const getStatusColor = () => {
    if (isLoading) return "bg-yellow-100 text-yellow-800";
    if (ollamaStatus?.status === "connected") return "bg-green-100 text-green-800";
    return "bg-red-100 text-red-800";
  };

  // Get models that are supported but not yet installed
  const missingModels = modelData?.supported_models?.filter(
    (model) => !modelData.available_models.includes(model)
  ) || [];

  return (
    <div className="flex items-center gap-4">
      {/* Ollama Status Indicator */}
      <div className="flex items-center gap-2">
        {getStatusIcon()}
        <Badge variant="secondary" className={`${getStatusColor()} border-0`}>
          Ollama {getStatusText()}
        </Badge>
      </div>

      {/* Model Selector */}
      {modelData && (
        <div className="flex items-center gap-2">
          <Cpu className="h-4 w-4 text-muted-foreground" />

          {/* Available Models Dropdown */}
          {modelData.available_models.length > 0 && (
            <Select
              value={modelData.current_model}
              onValueChange={handleModelChange}
              disabled={isSwitching || ollamaStatus?.status !== "connected"}
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select model" />
              </SelectTrigger>
              <SelectContent>
                {modelData.available_models.map((model) => (
                  <SelectItem key={model} value={model}>
                    {model}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}

          {/* Status Messages */}
          {isSwitching && (
            <span className="text-sm text-muted-foreground">Switching...</span>
          )}

          {isPulling && (
            <span className="text-sm text-muted-foreground">
              Downloading {pullingModel}...
            </span>
          )}

          {/* Pull Missing Models Button */}
          {missingModels.length > 0 && ollamaStatus?.status === "connected" && !isPulling && (
            <div className="flex items-center gap-1">
              {missingModels.slice(0, 2).map((model) => (
                <Button
                  key={model}
                  size="sm"
                  variant="outline"
                  onClick={() => handleModelPull(model)}
                  disabled={isSwitching}
                  className="h-8 px-2 text-xs"
                >
                  <Download className="h-3 w-3 mr-1" />
                  {model.split(':')[0]}
                </Button>
              ))}
              {missingModels.length > 2 && (
                <span className="text-xs text-muted-foreground">
                  +{missingModels.length - 2} more
                </span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}