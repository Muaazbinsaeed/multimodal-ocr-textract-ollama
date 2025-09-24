import { Moon, Sun, Scan } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";

export function Header() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Scan className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h1 className="text-lg font-semibold">OCR Text Extractor</h1>
              <p className="text-xs text-muted-foreground">Extract text from images</p>
            </div>
          </div>
          <div className="w-10 h-10" />
        </div>
      </header>
    );
  }

  return (
    <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Scan className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-lg font-semibold">OCR Text Extractor</h1>
            <p className="text-xs text-muted-foreground">Extract text from images</p>
          </div>
        </div>
        
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          className="h-10 w-10"
        >
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </div>
    </header>
  );
}