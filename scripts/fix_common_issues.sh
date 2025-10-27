
#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Fixing Common Setup Issues          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"

# Function to fix .env file
fix_env_file() {
    echo -e "\n${YELLOW}[1/4] Checking .env file...${NC}"
    
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Creating .env from .env.example...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env file${NC}"
        echo -e "${YELLOW}⚠️  Please update .env with your actual values${NC}"
    else
        echo -e "${GREEN}✅ .env file exists${NC}"
    fi
    
    # Fix ALLOWED_EXTENSIONS format
    if grep -q 'ALLOWED_EXTENSIONS=\["pdf","docx","txt"\]' .env 2>/dev/null; then
        echo -e "${YELLOW}Fixing ALLOWED_EXTENSIONS JSON format...${NC}"
        sed -i.bak 's/ALLOWED_EXTENSIONS=\["pdf","docx","txt"\]/ALLOWED_EXTENSIONS=["pdf", "docx", "txt"]/' .env
        echo -e "${GREEN}✅ Fixed ALLOWED_EXTENSIONS format${NC}"
    fi
}

# Function to kill processes on ports
kill_port_processes() {
    echo -e "\n${YELLOW}[2/4] Checking for port conflicts...${NC}"
    
    # Check and kill port 3000 (Frontend)
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}Killing process on port 3000...${NC}"
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true
        sleep 1
        echo -e "${GREEN}✅ Freed port 3000${NC}"
    else
        echo -e "${GREEN}✅ Port 3000 is available${NC}"
    fi
    
    # Check and kill port 8000 (Backend)
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}Killing process on port 8000...${NC}"
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 1
        echo -e "${GREEN}✅ Freed port 8000${NC}"
    else
        echo -e "${GREEN}✅ Port 8000 is available${NC}"
    fi
}

# Function to verify services
verify_services() {
    echo -e "\n${YELLOW}[3/4] Verifying required services...${NC}"
    
    # Check PostgreSQL
    if pg_isready -q 2>/dev/null; then
        echo -e "${GREEN}✅ PostgreSQL is running${NC}"
    else
        echo -e "${RED}❌ PostgreSQL is not running${NC}"
        echo -e "${YELLOW}   Start it with: brew services start postgresql${NC}"
    fi
    
    # Check Redis
    if redis-cli ping >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis is running${NC}"
    else
        echo -e "${RED}❌ Redis is not running${NC}"
        echo -e "${YELLOW}   Start it with: brew services start redis${NC}"
    fi
}

# Function to clean Python cache
clean_python_cache() {
    echo -e "\n${YELLOW}[4/4] Cleaning Python cache...${NC}"
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    echo -e "${GREEN}✅ Python cache cleaned${NC}"
}

# Run all fixes
fix_env_file
kill_port_processes
verify_services
clean_python_cache

echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Setup Issues Fixed!                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo -e "\n${GREEN}Next steps:${NC}"
echo -e "1. Update .env with your actual values (DB credentials, API keys, etc.)"
echo -e "2. Run: ${GREEN}./scripts/start_backend.sh${NC}"
echo -e "3. Run: ${GREEN}./scripts/start_celery.sh${NC} (in another terminal)"
echo -e "4. Run: ${GREEN}./scripts/start_frontend.sh${NC} (in another terminal)"
echo -e "\n${YELLOW}If you still have issues, check SETUP_LOCAL.md for detailed troubleshooting${NC}\n"
