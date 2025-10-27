#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║         JobFinder Pro - Local Setup Script               ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print step
print_step() {
    echo -e "\n${BLUE}==>${NC} ${GREEN}$1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to check if a port is in use
port_in_use() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        return 0 # Port is in use
    else
        return 1 # Port is not in use
    fi
}

# Step 1: Check prerequisites
print_step "Checking prerequisites..."

if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
print_success "Python $PYTHON_VERSION found"

if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

NODE_VERSION=$(node --version)
print_success "Node.js $NODE_VERSION found"

if ! command_exists psql; then
    print_warning "PostgreSQL client not found. Please install PostgreSQL 15+."
    print_warning "macOS: brew install postgresql@15"
    print_warning "Ubuntu: sudo apt-get install postgresql"
    exit 1
fi
print_success "PostgreSQL found"

if ! command_exists redis-cli; then
    print_warning "Redis not found. Please install Redis."
    print_warning "macOS: brew install redis"
    print_warning "Ubuntu: sudo apt-get install redis-server"
    exit 1
fi
print_success "Redis found"

# Step 2: Create .env file
print_step "Setting up environment file..."

if [ ! -f .env ]; then
    cp .env.example .env
    # Fix ALLOWED_EXTENSIONS format
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' 's/ALLOWED_EXTENSIONS=.*/ALLOWED_EXTENSIONS=["pdf","docx","txt"]/' .env
    else
        sed -i 's/ALLOWED_EXTENSIONS=.*/ALLOWED_EXTENSIONS=["pdf","docx","txt"]/' .env
    fi
    print_success ".env file created from .env.example"
else
    print_warning ".env file already exists, verifying format..."
    # Ensure ALLOWED_EXTENSIONS is in correct format
    if ! grep -q 'ALLOWED_EXTENSIONS=\["' .env; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' 's/ALLOWED_EXTENSIONS=.*/ALLOWED_EXTENSIONS=["pdf","docx","txt"]/' .env
        else
            sed -i 's/ALLOWED_EXTENSIONS=.*/ALLOWED_EXTENSIONS=["pdf","docx","txt"]/' .env
        fi
        print_success "Fixed ALLOWED_EXTENSIONS format"
    fi
fi

# Generate secure secrets if not present in .env
SECRET_KEY=$(grep '^SECRET_KEY=' .env | cut -d= -f2)
SESSION_SECRET=$(grep '^SESSION_SECRET=' .env | cut -d= -f2)

if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    else
        sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    fi
    print_success "Generated and added SECRET_KEY to .env"
fi

if [ -z "$SESSION_SECRET" ]; then
    SESSION_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/^SESSION_SECRET=.*/SESSION_SECRET=$SESSION_SECRET/" .env
    else
        sed -i "s/^SESSION_SECRET=.*/SESSION_SECRET=$SESSION_SECRET/" .env
    fi
    print_success "Generated and added SESSION_SECRET to .env"
fi


# Step 3: Create PostgreSQL database
print_step "Setting up PostgreSQL database..."

if psql -lqt | cut -d \| -f 1 | grep -qw jobfinder; then
    print_warning "Database 'jobfinder' already exists"
else
    createdb jobfinder 2>/dev/null || print_warning "Could not create database (may already exist)"
    print_success "PostgreSQL database 'jobfinder' created"
fi

# Step 4: Start Redis
print_step "Starting Redis..."

if redis-cli ping >/dev/null 2>&1; then
    print_success "Redis is already running"
else
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start redis >/dev/null 2>&1 || redis-server --daemonize yes
    else
        sudo systemctl start redis-server >/dev/null 2>&1 || redis-server --daemonize yes
    fi
    sleep 2
    if redis-cli ping >/dev/null 2>&1; then
        print_success "Redis started successfully"
    else
        print_error "Failed to start Redis"
        exit 1
    fi
fi

# Step 5: Install Python dependencies
print_step "Installing Python dependencies..."

python3 -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
print_success "Python dependencies installed"

# Step 6: Download spaCy model
print_step "Downloading spaCy language model..."

python3 -m spacy download en_core_web_sm --quiet
print_success "spaCy model downloaded"

# Step 7: Install frontend dependencies
print_step "Installing frontend dependencies..."

if [ -d "frontend" ]; then
    cd frontend
    npm install --silent
    cd ..
    print_success "Frontend dependencies installed"
else
    print_error "Frontend directory not found. Please ensure it exists."
    exit 1
fi

# Step 8: Run database migrations
print_step "Running database migrations..."

if command_exists alembic; then
    alembic upgrade head
    print_success "Database migrations completed"
else
    print_error "Alembic not found. Please install it: pip install alembic"
    exit 1
fi

# Step 9: Create admin user
print_step "Creating admin user..."

read -p "Create admin user? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Admin email: " ADMIN_EMAIL
    read -s -p "Admin password: " ADMIN_PASSWORD
    echo
    if python3 scripts/cli.py create-admin --email "$ADMIN_EMAIL" --password "$ADMIN_PASSWORD"; then
        print_success "Admin user created"
    else
        print_warning "Failed to create admin user (it might already exist)."
    fi
fi

# Step 10: Final summary
echo -e "\n${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Setup completed successfully! 🎉                   ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${BLUE}Next steps:${NC}"
echo -e "1. Review and update .env file if needed"
echo -e "2. Start development server: ${GREEN}./scripts/dev_start.sh${NC}"
echo -e "   Or manually:"
echo -e "   - Terminal 1 (Backend API): ${GREEN}uvicorn api.main:app --host 0.0.0.0 --port 5000 --reload${NC}"
echo -e "   - Terminal 2 (Celery Worker): ${GREEN}celery -A api.app.celery_app worker --loglevel=info${NC}"
echo -e "   - Terminal 3 (Frontend): ${GREEN}cd frontend && npm run dev${NC}"
echo -e "\n${BLUE}Access points:${NC}"
echo -e "- Frontend:  ${GREEN}http://localhost:3000${NC}"
echo -e "- API Docs:  ${GREEN}http://localhost:5000/docs${NC}"
echo -e "- Metrics:   ${GREEN}http://localhost:5000/metrics${NC}"
echo ""

# Troubleshooting section
echo -e "\n${BLUE}Troubleshooting:${NC}"
echo -e "  ${YELLOW}Issue: EADDRINUSE - Address already in use ${GREEN}0.0.0.0:5000${NC}"
echo -e "  ${YELLOW}Description:${NC} This error means that another process is already using port 5000."
echo -e "  ${YELLOW}Solution:${NC}"
echo -e "    1. Find the process using the port: ${GREEN}lsof -i :5000${NC}"
echo -e "    2. Kill the process (replace PID with the actual Process ID): ${GREEN}kill -9 <PID>${NC}"
echo -e "    3. If the issue persists, try changing the backend port in your .env file (e.g., API_PORT=5001)."
echo -e "       Then, restart the backend server with the new port: ${GREEN}uvicorn api.main:app --host 0.0.0.0 --port 5001 --reload${NC}"
echo -e "       Remember to update any other services that depend on this port."
echo ""
echo -e "  ${YELLOW}Issue: Frontend build or dependency errors${NC}"
echo -e "  ${YELLOW}Description:${NC} Problems during `npm install` or frontend startup."
echo -e "  ${YELLOW}Solution:${NC}"
echo -e "    1. Remove `node_modules` and `package-lock.json` in the `frontend` directory."
echo -e "    2. Clear npm cache: ${GREEN}npm cache clean --force${NC}"
echo -e "    3. Reinstall dependencies: ${GREEN}cd frontend && npm install && cd ..${NC}"
echo -e "    4. If the problem persists, check Node.js and npm versions. Ensure they meet the requirements."
echo ""
echo -e "  ${YELLOW}Issue: Database connection errors${NC}"
echo -e "  ${YELLOW}Description:${NC} Problems connecting to PostgreSQL."
echo -e "  ${YELLOW}Solution:${NC}"
echo -e "    1. Ensure PostgreSQL is running: ${GREEN}systemctl status postgresql${NC} (or equivalent command)."
echo -e "    2. Verify database credentials in your .env file (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)."
echo -e "    3. Check if the database `jobfinder` exists: ${GREEN}psql -l | grep jobfinder${NC}"
echo -e "    4. Try dropping and recreating the database if issues persist (use with caution): ${GREEN}dropdb jobfinder && createdb jobfinder${NC}"
echo ""
echo -e "  ${YELLOW}Issue: Redis connection errors${NC}"
echo -e "  ${YELLOW}Description:${NC} Problems connecting to Redis."
echo -e "  ${YELLOW}Solution:${NC}"
echo -e "    1. Ensure Redis is running: ${GREEN}redis-cli ping${NC}"
echo -e "    2. If not running, start it: ${GREEN}brew services start redis${NC} (macOS) or ${GREEN}sudo systemctl start redis-server${NC} (Ubuntu)."
echo ""
echo -e "  ${YELLOW}Issue: Missing Python dependencies or modules${NC}"
echo -e "  ${YELLOW}Description:${NC} Errors related to missing Python packages (e.g., `ModuleNotFoundError`)."
echo -e "  ${YELLOW}Solution:${NC}"
echo -e "    1. Ensure you are in the correct virtual environment. Activate it: ${GREEN}source venv/bin/activate${NC}"
echo -e "    2. Reinstall dependencies: ${GREEN}pip install -r requirements.txt${NC}"
echo -e "    3. Ensure the correct Python version is used."
echo ""