
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
print_step "Setting up environment variables..."

if [ ! -f .env ]; then
    cp .env.example .env
    
    # Generate secure secrets
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    SESSION_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Update .env with generated secrets
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
        sed -i '' "s|SESSION_SECRET=.*|SESSION_SECRET=$SESSION_SECRET|" .env
    else
        sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
        sed -i "s|SESSION_SECRET=.*|SESSION_SECRET=$SESSION_SECRET|" .env
    fi
    
    print_success "Created .env file with secure secrets"
else
    print_warning ".env file already exists, skipping creation"
fi

# Step 3: Create PostgreSQL database
print_step "Setting up PostgreSQL database..."

# Check if database exists
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

cd frontend
npm install --silent
cd ..
print_success "Frontend dependencies installed"

# Step 8: Run database migrations
print_step "Running database migrations..."

alembic upgrade head
print_success "Database migrations completed"

# Step 9: Create admin user
print_step "Creating admin user..."

read -p "Create admin user? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Admin email: " ADMIN_EMAIL
    read -s -p "Admin password: " ADMIN_PASSWORD
    echo
    python3 scripts/cli.py create-admin --email "$ADMIN_EMAIL" --password "$ADMIN_PASSWORD" || print_warning "Admin user may already exist"
fi

# Step 10: Final summary
echo -e "\n${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Setup completed successfully! 🎉                   ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${BLUE}Next steps:${NC}"
echo -e "1. Review and update .env file if needed"
echo -e "2. Start development server: ${GREEN}./scripts/dev_start.sh${NC}"
echo -e "   Or manually:"
echo -e "   - Terminal 1: ${GREEN}uvicorn api.main:app --host 0.0.0.0 --port 5000 --reload${NC}"
echo -e "   - Terminal 2: ${GREEN}celery -A api.app.celery_app worker --loglevel=info${NC}"
echo -e "   - Terminal 3: ${GREEN}cd frontend && npm run dev${NC}"
echo -e "\n${BLUE}Access points:${NC}"
echo -e "- Frontend:  ${GREEN}http://localhost:3000${NC}"
echo -e "- API Docs:  ${GREEN}http://localhost:5000/docs${NC}"
echo -e "- Metrics:   ${GREEN}http://localhost:5000/metrics${NC}"
echo ""
