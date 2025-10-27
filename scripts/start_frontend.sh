
#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Starting Frontend Application        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ frontend directory not found${NC}"
    exit 1
fi

cd frontend

echo -e "\n${YELLOW}Installing frontend dependencies...${NC}"
npm install --silent

# Check if port 3000 is already in use
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}❌ Port 3000 is already in use${NC}"
    echo -e "${YELLOW}Finding and killing process on port 3000...${NC}"
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

echo -e "\n${GREEN}✅ Starting Frontend on port 3000...${NC}"
echo -e "${BLUE}Frontend: http://0.0.0.0:3000${NC}\n"

npm run dev
