#!/bin/bash

# Restart All Services Script
# Stops and then starts all services

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔄 Restarting Multimodal OCR Services${NC}"
echo "====================================="

# Stop all services
echo -e "\n${YELLOW}Phase 1: Stopping services...${NC}"
bash scripts/stop.sh

# Wait a moment
echo -e "\n${YELLOW}Waiting for clean shutdown...${NC}"
sleep 3

# Start all services
echo -e "\n${YELLOW}Phase 2: Starting services...${NC}"
bash scripts/start.sh

echo -e "\n${GREEN}🎉 Restart completed!${NC}"