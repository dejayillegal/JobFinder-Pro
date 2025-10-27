
#!/bin/bash

set -e

echo "🚀 Starting JobFinder Pro in Production Mode"
echo "============================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo -e "${RED}❌ .env.production file not found${NC}"
    echo -e "${YELLOW}Creating from .env.example...${NC}"
    cp .env.example .env.production
    echo -e "${GREEN}✅ Created .env.production - please configure it before continuing${NC}"
    exit 1
fi

# Load production environment
export $(cat .env.production | xargs)

# Verify PostgreSQL is running
echo -e "\n${YELLOW}Checking PostgreSQL...${NC}"
if ! pg_isready -q; then
    echo -e "${RED}❌ PostgreSQL is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✅ PostgreSQL is running${NC}"

# Verify Redis is running
echo -e "\n${YELLOW}Checking Redis...${NC}"
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${RED}❌ Redis is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Redis is running${NC}"

# Run migrations
echo -e "\n${YELLOW}Running database migrations...${NC}"
alembic upgrade head
echo -e "${GREEN}✅ Migrations complete${NC}"

# Build frontend
echo -e "\n${YELLOW}Building frontend...${NC}"
cd frontend
npm run build
cd ..
echo -e "${GREEN}✅ Frontend built${NC}"

# Create logs directory
mkdir -p logs

echo -e "\n${GREEN}============================================="
echo -e "Starting services..."
echo -e "=============================================${NC}"

# Start services in background
echo -e "\n${YELLOW}Starting API server on port 8000...${NC}"
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4 > logs/api.log 2>&1 &
API_PID=$!

echo -e "${YELLOW}Starting Celery worker...${NC}"
celery -A api.app.celery_app worker --loglevel=info --concurrency=4 > logs/celery.log 2>&1 &
CELERY_PID=$!

echo -e "${YELLOW}Starting frontend on port 5000...${NC}"
cd frontend
npm run start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for services to start
sleep 3

echo -e "\n${GREEN}============================================="
echo -e "🎉 JobFinder Pro is running in production mode!"
echo -e "=============================================${NC}"
echo -e "\nAccess points:"
echo -e "- Frontend:  ${GREEN}http://localhost:5000${NC}"
echo -e "- API:       ${GREEN}http://localhost:8000${NC}"
echo -e "- API Docs:  ${GREEN}http://localhost:8000/docs${NC}"
echo -e "- Metrics:   ${GREEN}http://localhost:8000/metrics${NC}"
echo -e "\nProcess IDs:"
echo -e "- API:      ${API_PID}"
echo -e "- Celery:   ${CELERY_PID}"
echo -e "- Frontend: ${FRONTEND_PID}"
echo -e "\nTo stop services:"
echo -e "  kill ${API_PID} ${CELERY_PID} ${FRONTEND_PID}"
echo -e "\nLogs location: ./logs/"
echo ""

# Save PIDs to file for easy cleanup
echo "${API_PID} ${CELERY_PID} ${FRONTEND_PID}" > .production_pids

echo -e "${YELLOW}Services are running in the background${NC}"
echo -e "${YELLOW}To stop: ./scripts/production_stop.sh${NC}"
