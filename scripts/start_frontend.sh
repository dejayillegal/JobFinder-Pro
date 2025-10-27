
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

echo -e "\n${GREEN}✅ Starting Frontend on port 5000...${NC}"
echo -e "${BLUE}Frontend: http://0.0.0.0:5000${NC}\n"

npm run dev
