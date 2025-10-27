#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Starting Backend API Server         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo -e "${YELLOW}Run: cp .env.example .env and configure it${NC}"
    exit 1
fi

# Load environment (properly handle values with special characters)
set -a
source .env
set +a

echo -e "\n${YELLOW}Checking Python dependencies...${NC}"
pip install -q -r requirements.txt

echo -e "${YELLOW}Downloading spaCy model (if needed)...${NC}"
python -m spacy download en_core_web_sm --quiet 2>/dev/null || echo -e "${YELLOW}⚠️  spaCy model already installed or skipped${NC}"

echo -e "\n${YELLOW}Running database migrations...${NC}"
alembic upgrade head

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}❌ Port 8000 is already in use${NC}"
    echo -e "${YELLOW}Finding and killing process on port 8000...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

echo -e "\n${GREEN}✅ Starting Backend API Server on port 8000...${NC}"
echo -e "${BLUE}API Docs: http://0.0.0.0:8000/docs${NC}"
echo -e "${BLUE}Health: http://0.0.0.0:8000/api/health${NC}\n"

uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload