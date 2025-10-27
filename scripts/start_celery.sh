
#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Starting Celery Worker               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file. Please configure it.${NC}"
fi

# Export environment variables properly
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

echo -e "\n${YELLOW}Checking Redis connection...${NC}"
if command -v redis-cli &> /dev/null && redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${RED}❌ Redis is not running${NC}"
    echo -e "${YELLOW}Start Redis with: redis-server${NC}"
    echo -e "${YELLOW}Or use Replit's Redis if available${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ Starting Celery Worker...${NC}\n"

# Run Celery with proper module path
celery -A api.app.celery_app worker --loglevel=info --pool=solo
