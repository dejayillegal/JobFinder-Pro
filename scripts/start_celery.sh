
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
    echo -e "${YELLOW}Run: cp .env.example .env and configure it${NC}"
    exit 1
fi

# Load environment (properly handle values with special characters)
set -a
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip empty lines and comments
    if [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    # Only export valid variable assignments
    if [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
        export "$line"
    fi
done < .env
set +a

echo -e "\n${YELLOW}Checking Redis connection...${NC}"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${RED}❌ Redis is not running${NC}"
    echo -e "${YELLOW}Start Redis with: redis-server${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ Starting Celery Worker...${NC}\n"

celery -A api.app.celery_app worker --loglevel=info
