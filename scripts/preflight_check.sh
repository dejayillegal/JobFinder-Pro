#!/bin/bash

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Pre-flight Environment Check         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

ERRORS=0

# Check 1: .env file exists
echo -e "${YELLOW}[1/6] Checking .env file...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo -e "${YELLOW}Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Check 2: ALLOWED_EXTENSIONS format
echo -e "\n${YELLOW}[2/6] Checking ALLOWED_EXTENSIONS format...${NC}"
if grep -q 'ALLOWED_EXTENSIONS=\["pdf", "docx", "txt"\]' .env; then
    echo -e "${GREEN}✓ ALLOWED_EXTENSIONS has valid JSON format${NC}"
else
    echo -e "${YELLOW}Fixing ALLOWED_EXTENSIONS format...${NC}"
    sed -i.bak 's/ALLOWED_EXTENSIONS=.*/ALLOWED_EXTENSIONS=["pdf", "docx", "txt"]/' .env
    echo -e "${GREEN}✓ Fixed ALLOWED_EXTENSIONS format${NC}"
fi

# Check 3: Port availability
echo -e "\n${YELLOW}[3/6] Checking port availability...${NC}"
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port 3000 is in use${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ Port 3000 is available${NC}"
fi

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port 8000 is in use${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ Port 8000 is available${NC}"
fi

# Continue with other checks
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port 3000 is in use${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ Port 3000 is available${NC}"
fi

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}❌ Port 8000 is in use${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ Port 8000 is available${NC}"
fi

# Check 4: PostgreSQL
echo -e "\n${YELLOW}[4/6] Checking PostgreSQL...${NC}"
if pg_isready >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${RED}❌ PostgreSQL is not running${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 5: Redis
echo -e "\n${YELLOW}[5/6] Checking Redis...${NC}"
if redis-cli ping >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${RED}❌ Redis is not running${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 6: Python dependencies
echo -e "\n${YELLOW}[6/6] Checking Python environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
else
    echo -e "${RED}❌ Virtual environment not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Summary
echo -e "\n${BLUE}════════════════════════════════════════${NC}"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Ready to start services.${NC}"
    exit 0
else
    echo -e "${RED}✗ $ERRORS check(s) failed. Please fix the issues above.${NC}"
    exit 1
fi