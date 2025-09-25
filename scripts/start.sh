#!/bin/bash

# Start All Services Script
# Starts Ollama, Backend, and Frontend services

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Multimodal OCR Services${NC}"
echo "=================================="

# Create logs directory
mkdir -p logs

# Start Ollama
echo -e "\n${BLUE}🤖 Starting Ollama...${NC}"
if ! pgrep -f "ollama serve" > /dev/null; then
    nohup ollama serve > logs/ollama.log 2>&1 &
    echo "✅ Ollama service started"

    # Wait for Ollama to be ready
    echo "   Waiting for Ollama to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo "✅ Ollama is ready"
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ Ollama failed to start${NC}"
            exit 1
        fi
    done
else
    echo "✅ Ollama already running"
fi

# Start Backend
echo -e "\n${BLUE}⚙️  Starting Backend...${NC}"
if ! pgrep -f "uvicorn app.main:app" > /dev/null; then
    cd backend
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
    cd ..
    echo "✅ Backend service started"

    # Wait for backend to be ready
    echo "   Waiting for backend to be ready..."
    for i in {1..15}; do
        if curl -s http://localhost:8000/healthz > /dev/null 2>&1; then
            echo "✅ Backend is ready"
            break
        fi
        sleep 1
        if [ $i -eq 15 ]; then
            echo -e "${YELLOW}⚠️  Backend taking longer than expected${NC}"
            break
        fi
    done
else
    echo "✅ Backend already running"
fi

# Start Frontend
echo -e "\n${BLUE}🎨 Starting Frontend...${NC}"
if ! pgrep -f "npm run dev" > /dev/null; then
    cd frontend
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    cd ..
    echo "✅ Frontend service started"

    # Wait a bit for frontend to start
    sleep 3
    echo "✅ Frontend is ready"
else
    echo "✅ Frontend already running"
fi

echo -e "\n${GREEN}🎉 All services started successfully!${NC}"
echo "=================================="
echo -e "Frontend:  ${BLUE}http://localhost:8080${NC}"
echo -e "Backend:   ${BLUE}http://localhost:8000${NC}"
echo -e "API Docs:  ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "To view logs:"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/frontend.log"
echo "  tail -f logs/ollama.log"
echo ""
echo "To stop services: bash scripts/stop.sh"