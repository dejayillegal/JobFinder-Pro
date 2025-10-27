#!/bin/bash

set -e

echo "🚀 Starting JobFinder Pro Development Environment"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file. Please edit it with your configuration.${NC}"
    exit 1
fi

# Check PostgreSQL
echo -e "\n${YELLOW}Checking PostgreSQL...${NC}"
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL is installed${NC}"
else
    echo -e "${RED}❌ PostgreSQL not found. Please install PostgreSQL.${NC}"
    exit 1
fi

# Check Redis
echo -e "\n${YELLOW}Checking Redis...${NC}"
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✅ Redis is running${NC}"
    else
        echo -e "${YELLOW}⚠️  Starting Redis...${NC}"
        redis-server --daemonize yes
    fi
else
    echo -e "${RED}❌ Redis not found. Please install Redis.${NC}"
    exit 1
fi

# Install Python dependencies
echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Python dependencies installed${NC}"

# Download spaCy model
echo -e "\n${YELLOW}Downloading spaCy model...${NC}"
python -m spacy download en_core_web_sm --quiet
echo -e "${GREEN}✅ spaCy model downloaded${NC}"

# Run database migrations
echo -e "\n${YELLOW}Running database migrations...${NC}"
alembic upgrade head
echo -e "${GREEN}✅ Database migrations complete${NC}"

# Install frontend dependencies
echo -e "\n${YELLOW}Installing frontend dependencies...${NC}"
cd frontend
npm install --silent
cd ..
echo -e "${GREEN}✅ Frontend dependencies installed${NC}"

# Start services in the background
echo -e "\n${YELLOW}Starting services...${NC}"

# Start API server
echo -e "${GREEN}Starting API server on port 5000...${NC}"
uvicorn api.main:app --host 0.0.0.0 --port 5000 --reload &
API_PID=$!

# Start Celery worker
echo -e "${GREEN}Starting Celery worker...${NC}"
celery -A api.app.celery_app worker --loglevel=info &
CELERY_PID=$!

# Start frontend
echo -e "${GREEN}Starting frontend on port 3000...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $API_PID $CELERY_PID $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ All services stopped${NC}"
}

trap cleanup EXIT

echo -e "\n${GREEN}=================================================="
echo -e "🎉 JobFinder Pro is running!"
echo -e "=================================================="
echo -e "Frontend:    http://localhost:3000"
echo -e "API Docs:    http://localhost:5000/docs"
echo -e "Metrics:     http://localhost:5000/metrics"
echo -e "=================================================="
echo -e "Press Ctrl+C to stop all services${NC}\n"

# Wait for user interrupt
wait
