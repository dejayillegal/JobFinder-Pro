
#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Starting Database Services           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Start PostgreSQL
echo -e "\n${YELLOW}Starting PostgreSQL...${NC}"
if command_exists pg_isready; then
    if pg_isready -q; then
        echo -e "${GREEN}✅ PostgreSQL is already running${NC}"
    else
        # Try to start PostgreSQL based on OS
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew services start postgresql@15
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo systemctl start postgresql
        fi
        
        # Wait for PostgreSQL to start
        sleep 2
        
        if pg_isready -q; then
            echo -e "${GREEN}✅ PostgreSQL started${NC}"
        else
            echo -e "${RED}❌ Failed to start PostgreSQL${NC}"
            exit 1
        fi
    fi
else
    echo -e "${RED}❌ PostgreSQL not installed${NC}"
    exit 1
fi

# Start Redis
echo -e "\n${YELLOW}Starting Redis...${NC}"
if command_exists redis-cli; then
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis is already running${NC}"
    else
        # Try to start Redis based on OS
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew services start redis
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo systemctl start redis-server
        else
            redis-server --daemonize yes
        fi
        
        # Wait for Redis to start
        sleep 2
        
        if redis-cli ping > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Redis started${NC}"
        else
            echo -e "${RED}❌ Failed to start Redis${NC}"
            exit 1
        fi
    fi
else
    echo -e "${RED}❌ Redis not installed${NC}"
    exit 1
fi

echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Database Services Running            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo -e "\n${BLUE}PostgreSQL Status:${NC}"
pg_isready
echo -e "\n${BLUE}Redis Status:${NC}"
redis-cli ping

echo -e "\n${YELLOW}Keep this terminal open to maintain database services${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop services${NC}\n"

# Keep script running
tail -f /dev/null
