#!/bin/bash

# Stop All Services Script
# Stops Ollama, Backend, and Frontend services

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🛑 Stopping Multimodal OCR Services${NC}"
echo "==================================="

# Stop Frontend (npm processes)
echo -e "\n${BLUE}🎨 Stopping Frontend...${NC}"
if pgrep -f "npm run dev" > /dev/null; then
    pkill -f "npm run dev" && echo "✅ Frontend stopped" || echo -e "${YELLOW}⚠️  Frontend process not found${NC}"
else
    echo "✅ Frontend not running"
fi

# Stop Frontend (Vite processes)
if pgrep -f "vite" > /dev/null; then
    pkill -f "vite" && echo "✅ Vite stopped" || echo -e "${YELLOW}⚠️  Vite process not found${NC}"
fi

# Stop processes on frontend port
if lsof -ti:8080 > /dev/null 2>&1; then
    echo "   Stopping processes on port 8080..."
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
fi

# Stop Backend (uvicorn processes)
echo -e "\n${BLUE}⚙️  Stopping Backend...${NC}"
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    pkill -f "uvicorn app.main:app" && echo "✅ Backend stopped" || echo -e "${YELLOW}⚠️  Backend process not found${NC}"
else
    echo "✅ Backend not running"
fi

# Stop processes on backend port
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "   Stopping processes on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
fi

# Stop Ollama
echo -e "\n${BLUE}🤖 Stopping Ollama...${NC}"
if pgrep -f "ollama serve" > /dev/null; then
    pkill -f "ollama serve" && echo "✅ Ollama stopped" || echo -e "${YELLOW}⚠️  Ollama process not found${NC}"
else
    echo "✅ Ollama not running"
fi

# Stop processes on ollama port
if lsof -ti:11434 > /dev/null 2>&1; then
    echo "   Stopping processes on port 11434..."
    lsof -ti:11434 | xargs kill -9 2>/dev/null || true
fi

# Clean up any remaining Python processes from our project
echo -e "\n${BLUE}🧹 Cleanup...${NC}"
pkill -f "python.*app.main" 2>/dev/null && echo "✅ Cleanup completed" || echo "✅ No cleanup needed"

echo -e "\n${GREEN}🎉 All services stopped successfully!${NC}"
echo "Logs are preserved in the logs/ directory."