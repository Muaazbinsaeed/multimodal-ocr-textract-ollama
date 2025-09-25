#!/bin/bash

# Docker Control Script
# Manage Docker containers for the Multimodal OCR application

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

show_help() {
    echo -e "${BLUE}Docker Control Script${NC}"
    echo "====================="
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  up      Start all services with Docker Compose"
    echo "  down    Stop all Docker services"
    echo "  restart Restart all Docker services"
    echo "  build   Build Docker images"
    echo "  logs    Show logs from all services"
    echo "  status  Show status of all containers"
    echo "  pull    Pull Ollama models"
    echo "  clean   Remove all containers and volumes"
    echo "  help    Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 up        # Start all services"
    echo "  $0 logs      # View all logs"
    echo "  $0 pull      # Pull required models"
}

docker_up() {
    echo -e "${BLUE}🚀 Starting Docker services...${NC}"

    if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        exit 1
    fi

    # Use docker compose or docker-compose based on availability
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        DOCKER_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_CMD="docker-compose"
    else
        echo -e "${RED}❌ Docker Compose is not available${NC}"
        exit 1
    fi

    $DOCKER_CMD up --build -d

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ All services started successfully${NC}"
        echo ""
        echo "Services are now running:"
        echo -e "Frontend:  ${BLUE}http://localhost:8080${NC}"
        echo -e "Backend:   ${BLUE}http://localhost:8000${NC}"
        echo -e "API Docs:  ${BLUE}http://localhost:8000/docs${NC}"
        echo -e "Ollama:    ${BLUE}http://localhost:11434${NC}"
        echo ""
        echo "To pull models: $0 pull"
        echo "To view logs: $0 logs"
    else
        echo -e "${RED}❌ Failed to start services${NC}"
        exit 1
    fi
}

docker_down() {
    echo -e "${BLUE}🛑 Stopping Docker services...${NC}"

    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        docker compose down
    elif command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        echo -e "${RED}❌ Docker Compose is not available${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ All services stopped${NC}"
}

docker_restart() {
    echo -e "${BLUE}🔄 Restarting Docker services...${NC}"
    docker_down
    sleep 2
    docker_up
}

docker_build() {
    echo -e "${BLUE}🔨 Building Docker images...${NC}"

    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        docker compose build
    elif command -v docker-compose &> /dev/null; then
        docker-compose build
    else
        echo -e "${RED}❌ Docker Compose is not available${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Build completed${NC}"
}

docker_logs() {
    echo -e "${BLUE}📋 Showing Docker logs...${NC}"

    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        docker compose logs -f
    elif command -v docker-compose &> /dev/null; then
        docker-compose logs -f
    else
        echo -e "${RED}❌ Docker Compose is not available${NC}"
        exit 1
    fi
}

docker_status() {
    echo -e "${BLUE}📊 Container status:${NC}"
    echo ""
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

docker_pull_models() {
    echo -e "${BLUE}📥 Pulling Ollama models...${NC}"

    # Check if ollama container is running
    if ! docker ps | grep -q ollama; then
        echo -e "${RED}❌ Ollama container is not running. Start services first.${NC}"
        exit 1
    fi

    # Read models from models.txt and pull each one
    if [ -f "models.txt" ]; then
        echo "Reading models from models.txt..."
        while IFS= read -r model || [ -n "$model" ]; do
            # Skip comments and empty lines
            if [[ "$model" =~ ^[[:space:]]*# ]] || [[ -z "$model" ]]; then
                continue
            fi

            # Trim whitespace
            model=$(echo "$model" | xargs)

            if [ -n "$model" ]; then
                echo "Pulling model: $model"
                docker exec -it multimodal-ocr-textract-ollama-ollama-1 ollama pull "$model"
            fi
        done < "models.txt"
    else
        echo "models.txt not found, pulling default models..."
        docker exec -it multimodal-ocr-textract-ollama-ollama-1 ollama pull moondream:1.8b
        docker exec -it multimodal-ocr-textract-ollama-ollama-1 ollama pull llava:latest
        docker exec -it multimodal-ocr-textract-ollama-ollama-1 ollama pull llama3.2-vision:latest
    fi

    echo -e "${GREEN}✅ Models pulled successfully${NC}"
}

docker_clean() {
    echo -e "${YELLOW}⚠️  This will remove all containers and volumes. Continue? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo -e "${BLUE}🧹 Cleaning up Docker resources...${NC}"

        if command -v docker &> /dev/null && docker compose version &> /dev/null; then
            docker compose down -v --remove-orphans
        elif command -v docker-compose &> /dev/null; then
            docker-compose down -v --remove-orphans
        fi

        # Remove any dangling images
        docker image prune -f

        echo -e "${GREEN}✅ Cleanup completed${NC}"
    else
        echo "Cancelled."
    fi
}

# Main script logic
case "$1" in
    up)
        docker_up
        ;;
    down)
        docker_down
        ;;
    restart)
        docker_restart
        ;;
    build)
        docker_build
        ;;
    logs)
        docker_logs
        ;;
    status)
        docker_status
        ;;
    pull)
        docker_pull_models
        ;;
    clean)
        docker_clean
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac