#!/bin/bash

# Multimodal OCR Setup Script
# Complete setup for backend, frontend, and Ollama

set -e  # Exit on any error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
MODELS_FILE="models.txt"
OLLAMA_HOST="http://localhost:11434"
BACKEND_PORT=8000
FRONTEND_PORT=8080

echo -e "${BLUE}🚀 Multimodal OCR Setup Script${NC}"
echo "=================================="

# Check system requirements
check_requirements() {
    echo -e "\n${BLUE}📋 Checking system requirements...${NC}"

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo -e "✅ Python $PYTHON_VERSION found"
    else
        echo -e "${RED}❌ Python 3.11+ required${NC}"
        exit 1
    fi

    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        echo -e "✅ Node.js $NODE_VERSION found"
    else
        echo -e "${RED}❌ Node.js 18+ required${NC}"
        exit 1
    fi

    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        echo -e "✅ npm $NPM_VERSION found"
    else
        echo -e "${RED}❌ npm required${NC}"
        exit 1
    fi
}

# Kill existing processes
cleanup_processes() {
    echo -e "\n${YELLOW}🧹 Cleaning up existing processes...${NC}"

    # Kill processes on backend port
    if lsof -ti:$BACKEND_PORT &> /dev/null; then
        echo "   Stopping backend processes on port $BACKEND_PORT..."
        lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
    fi

    # Kill processes on frontend port
    if lsof -ti:$FRONTEND_PORT &> /dev/null; then
        echo "   Stopping frontend processes on port $FRONTEND_PORT..."
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
    fi

    # Kill any remaining uvicorn processes
    pkill -f "uvicorn app.main:app" 2>/dev/null || true

    # Kill any remaining npm dev processes
    pkill -f "npm run dev" 2>/dev/null || true

    echo "✅ Process cleanup completed"
}

# Setup and start Ollama
setup_ollama() {
    echo -e "\n${BLUE}🤖 Setting up Ollama...${NC}"

    # Check if Ollama is installed
    if ! command -v ollama &> /dev/null; then
        echo "   Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        echo "✅ Ollama already installed"
    fi

    # Check if Ollama is running
    if ! curl -s $OLLAMA_HOST/api/tags &> /dev/null; then
        echo "   Starting Ollama service..."
        # Start Ollama in the background
        nohup ollama serve > /dev/null 2>&1 &

        # Wait for Ollama to start
        echo "   Waiting for Ollama to start..."
        for i in {1..30}; do
            if curl -s $OLLAMA_HOST/api/tags &> /dev/null; then
                echo "✅ Ollama service is running"
                break
            fi
            sleep 1
            if [ $i -eq 30 ]; then
                echo -e "${RED}❌ Ollama failed to start${NC}"
                exit 1
            fi
        done
    else
        echo "✅ Ollama service is already running"
    fi
}

# Pull models from models.txt
pull_models() {
    echo -e "\n${BLUE}📥 Pulling models from $MODELS_FILE...${NC}"

    if [ ! -f "$MODELS_FILE" ]; then
        echo -e "${RED}❌ $MODELS_FILE not found${NC}"
        return 1
    fi

    # Read models from file (skip comments and empty lines)
    while IFS= read -r model || [ -n "$model" ]; do
        # Skip comments and empty lines
        if [[ "$model" =~ ^[[:space:]]*# ]] || [[ -z "$model" ]]; then
            continue
        fi

        # Trim whitespace
        model=$(echo "$model" | xargs)

        if [ -n "$model" ]; then
            echo "   Pulling model: $model"
            if ollama pull "$model"; then
                echo "   ✅ $model pulled successfully"
            else
                echo -e "   ${YELLOW}⚠️  Failed to pull $model (might not exist)${NC}"
            fi
        fi
    done < "$MODELS_FILE"

    # List available models
    echo -e "\n📋 Available models:"
    ollama list
}

# Setup backend
setup_backend() {
    echo -e "\n${BLUE}⚙️  Setting up backend...${NC}"

    cd "$BACKEND_DIR"

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "   Creating Python virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install dependencies
    echo "   Installing backend dependencies..."
    pip install --upgrade pip
    pip install -e .

    # Create .env from .env.example if it doesn't exist
    if [ ! -f ".env" ] && [ -f ".env.example" ]; then
        echo "   Creating .env from .env.example..."
        cp .env.example .env
    fi

    cd ..
    echo "✅ Backend setup completed"
}

# Setup frontend
setup_frontend() {
    echo -e "\n${BLUE}🎨 Setting up frontend...${NC}"

    cd "$FRONTEND_DIR"

    # Install dependencies
    echo "   Installing frontend dependencies..."
    npm install

    # Build frontend (optional)
    if [ "$1" = "--build" ]; then
        echo "   Building frontend..."
        npm run build
    fi

    cd ..
    echo "✅ Frontend setup completed"
}

# Start services
start_services() {
    echo -e "\n${BLUE}🚀 Starting services...${NC}"

    # Start backend
    echo "   Starting backend server..."
    cd "$BACKEND_DIR"
    source venv/bin/activate
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..

    # Wait a bit for backend to start
    sleep 3

    # Check backend health
    if curl -s http://localhost:$BACKEND_PORT/healthz &> /dev/null; then
        echo "✅ Backend server started (PID: $BACKEND_PID)"
    else
        echo -e "${RED}❌ Backend server failed to start${NC}"
        exit 1
    fi

    # Start frontend
    echo "   Starting frontend server..."
    cd "$FRONTEND_DIR"
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..

    # Wait a bit for frontend to start
    sleep 5

    echo "✅ Frontend server started (PID: $FRONTEND_PID)"
}

# Run tests
run_tests() {
    echo -e "\n${BLUE}🧪 Running API tests...${NC}"

    # Wait for services to be fully ready
    sleep 2

    # Run Python test suite
    if [ -f "tests/api_test.py" ]; then
        echo "   Running Python test suite..."
        python3 tests/api_test.py
    fi

    # Run shell test suite
    if [ -f "tests/test_api.sh" ]; then
        echo "   Running shell test suite..."
        bash tests/test_api.sh
    fi
}

# Main execution
main() {
    # Create logs directory
    mkdir -p logs

    # Parse command line arguments
    BUILD_FRONTEND=false
    RUN_TESTS=false
    USE_DOCKER=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --build)
                BUILD_FRONTEND=true
                shift
                ;;
            --test)
                RUN_TESTS=true
                shift
                ;;
            --docker)
                USE_DOCKER=true
                shift
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --build    Build frontend for production"
                echo "  --test     Run API tests after setup"
                echo "  --docker   Use Docker instead of local setup"
                echo "  --help     Show this help message"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done

    # Docker setup
    if [ "$USE_DOCKER" = true ]; then
        echo -e "\n${BLUE}🐳 Using Docker setup...${NC}"
        if [ -f "docker-compose.yml" ]; then
            cleanup_processes
            docker-compose down
            docker-compose up --build -d
            echo "✅ Docker services started"

            if [ "$RUN_TESTS" = true ]; then
                sleep 10  # Wait for services to be ready
                run_tests
            fi
        else
            echo -e "${RED}❌ docker-compose.yml not found${NC}"
            exit 1
        fi
        return
    fi

    # Local setup
    check_requirements
    cleanup_processes
    setup_ollama
    pull_models
    setup_backend

    if [ "$BUILD_FRONTEND" = true ]; then
        setup_frontend --build
    else
        setup_frontend
    fi

    start_services

    if [ "$RUN_TESTS" = true ]; then
        run_tests
    fi

    # Show final status
    echo -e "\n${GREEN}🎉 Setup completed successfully!${NC}"
    echo "=================================="
    echo -e "Backend:  ${BLUE}http://localhost:$BACKEND_PORT${NC}"
    echo -e "Frontend: ${BLUE}http://localhost:$FRONTEND_PORT${NC}"
    echo -e "API Docs: ${BLUE}http://localhost:$BACKEND_PORT/docs${NC}"
    echo ""
    echo "To stop services:"
    echo "  pkill -f 'uvicorn app.main:app'"
    echo "  pkill -f 'npm run dev'"
    echo ""
    echo "To view logs:"
    echo "  tail -f logs/backend.log"
    echo "  tail -f logs/frontend.log"
}

# Run main function
main "$@"