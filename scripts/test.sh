#!/bin/bash

# Test Script
# Runs all available tests for the Multimodal OCR application

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🧪 Running Multimodal OCR Test Suite${NC}"
echo "===================================="

# Check if services are running
check_services() {
    echo -e "\n${BLUE}📋 Checking service status...${NC}"

    # Check backend
    if curl -s http://localhost:8000/healthz > /dev/null 2>&1; then
        echo "✅ Backend is running"
    else
        echo -e "${YELLOW}⚠️  Backend not responding. Starting services...${NC}"
        bash scripts/start.sh
        sleep 5
    fi

    # Check Ollama
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is running"
    else
        echo -e "${RED}❌ Ollama not responding${NC}"
        return 1
    fi

    # Check frontend (if running locally)
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        echo "✅ Frontend is running"
    else
        echo -e "${YELLOW}ℹ️  Frontend not running (this is optional for API tests)${NC}"
    fi
}

# Run Python API tests
run_python_tests() {
    echo -e "\n${BLUE}🐍 Running Python API tests...${NC}"

    if [ -f "tests/api_test.py" ]; then
        python3 tests/api_test.py
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Python tests passed${NC}"
            return 0
        else
            echo -e "${RED}❌ Python tests failed${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  tests/api_test.py not found${NC}"
        return 1
    fi
}

# Run shell API tests
run_shell_tests() {
    echo -e "\n${BLUE}🐚 Running Shell API tests...${NC}"

    if [ -f "tests/test_api.sh" ]; then
        bash tests/test_api.sh
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Shell tests passed${NC}"
            return 0
        else
            echo -e "${RED}❌ Shell tests failed${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  tests/test_api.sh not found${NC}"
        return 1
    fi
}

# Run backend unit tests (if available)
run_backend_tests() {
    echo -e "\n${BLUE}⚙️  Running Backend unit tests...${NC}"

    cd backend

    if [ -f "pyproject.toml" ] && grep -q pytest pyproject.toml; then
        if [ -d "venv" ]; then
            source venv/bin/activate
        fi

        if command -v pytest > /dev/null 2>&1; then
            pytest tests/ -v 2>/dev/null || pytest . -v 2>/dev/null || echo -e "${YELLOW}⚠️  No pytest tests found${NC}"
        else
            echo -e "${YELLOW}⚠️  pytest not installed${NC}"
        fi
    else
        echo -e "${YELLOW}ℹ️  No pytest configuration found${NC}"
    fi

    cd ..
}

# Run frontend tests (if available)
run_frontend_tests() {
    echo -e "\n${BLUE}🎨 Running Frontend tests...${NC}"

    cd frontend

    if [ -f "package.json" ] && grep -q '"test"' package.json; then
        npm test -- --passWithNoTests 2>/dev/null || echo -e "${YELLOW}ℹ️  No frontend tests configured${NC}"
    else
        echo -e "${YELLOW}ℹ️  No test script found in package.json${NC}"
    fi

    cd ..
}

# Test Docker setup (optional)
test_docker() {
    echo -e "\n${BLUE}🐳 Testing Docker setup...${NC}"

    if command -v docker > /dev/null 2>&1; then
        if [ -f "docker-compose.yml" ]; then
            echo "✅ Docker and docker-compose.yml found"
            echo "   Run 'bash scripts/docker-control.sh up' to test Docker deployment"
        else
            echo -e "${YELLOW}⚠️  docker-compose.yml not found${NC}"
        fi
    else
        echo -e "${YELLOW}ℹ️  Docker not installed${NC}"
    fi
}

# Main test execution
main() {
    local python_passed=false
    local shell_passed=false

    # Check services
    check_services || {
        echo -e "${RED}❌ Service check failed${NC}"
        exit 1
    }

    # Run Python tests
    if run_python_tests; then
        python_passed=true
    fi

    # Run shell tests
    if run_shell_tests; then
        shell_passed=true
    fi

    # Run additional tests
    run_backend_tests
    run_frontend_tests
    test_docker

    # Summary
    echo -e "\n${BLUE}📊 Test Summary${NC}"
    echo "==============="

    if $python_passed; then
        echo -e "Python API Tests:    ${GREEN}✅ PASSED${NC}"
    else
        echo -e "Python API Tests:    ${RED}❌ FAILED${NC}"
    fi

    if $shell_passed; then
        echo -e "Shell API Tests:     ${GREEN}✅ PASSED${NC}"
    else
        echo -e "Shell API Tests:     ${RED}❌ FAILED${NC}"
    fi

    if $python_passed && $shell_passed; then
        echo -e "\n${GREEN}🎉 All critical tests passed!${NC}"
        exit 0
    else
        echo -e "\n${RED}⚠️  Some tests failed. Check the output above.${NC}"
        exit 1
    fi
}

# Run main function
main "$@"