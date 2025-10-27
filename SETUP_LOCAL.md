# Local Development Setup Guide

This guide provides detailed instructions for setting up and running JobFinder Pro locally on your machine.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Database Setup](#3-database-setup)
  - [4. Frontend Setup](#4-frontend-setup)
  - [5. Redis Setup](#5-redis-setup)
- [Running the Application](#running-the-application)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 20+** and npm - [Download Node.js](https://nodejs.org/)
- **PostgreSQL 14+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **Redis 7+** - [Download Redis](https://redis.io/download/)
- **Git** - [Download Git](https://git-scm.com/downloads/)

### Verify Installation

```bash
python --version  # Should be 3.11 or higher
node --version    # Should be 20.x or higher
npm --version     # Should be 10.x or higher
psql --version    # Should be 14.x or higher
redis-cli --version  # Should be 7.x or higher
```

---

## Quick Start

For experienced developers, here's the fastest way to get started:

```bash
# 1. Clone and navigate
git clone <your-repo-url>
cd jobfinder-pro

# 2. Backend setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Database setup
createdb jobfinder_pro
cp .env.example .env  # Edit with your configuration
alembic upgrade head

# 4. Frontend setup
cd frontend
npm install
cd ..

# 5. Start services (3 separate terminals)
# Terminal 1 - Backend API
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Celery Worker
celery -A api.app.celery_app worker --loglevel=info

# Terminal 3 - Frontend
cd frontend && npm run dev
```

Visit http://localhost:3000 for the frontend and http://localhost:8000/docs for the API documentation.

---

## Detailed Setup

### 1. Clone the Repository

```bash
# Clone the repository
git clone <your-repo-url>
cd jobfinder-pro

# Create a new branch for your work (optional)
git checkout -b feature/my-feature
```

### 2. Backend Setup

#### 2.1 Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### 2.2 Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Download spaCy language model (required for resume parsing)
python -m spacy download en_core_web_sm
```

#### 2.3 Verify Backend Installation

```bash
# Check if FastAPI is installed correctly
python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')"

# Check if spaCy model is downloaded
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('spaCy model loaded successfully')"
```

### 3. Database Setup

#### 3.1 Create PostgreSQL Database

```bash
# Create a new database
createdb jobfinder_pro

# Or using psql:
psql -U postgres
CREATE DATABASE jobfinder_pro;
\q
```

#### 3.2 Configure Environment Variables

Create a `.env` file in the project root:

```bash


---

## Detailed Credential Setup Guide

### 1. Database Credentials (PostgreSQL)

**macOS Setup:**
```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Create database
createdb jobfinder

# Your DATABASE_URL will be:
DATABASE_URL=postgresql://localhost:5432/jobfinder
```

**Ubuntu/Linux Setup:**
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql

# Create database and user
sudo -u postgres createdb jobfinder
sudo -u postgres createuser -s $USER

# Your DATABASE_URL will be:
DATABASE_URL=postgresql://localhost:5432/jobfinder
```

**Windows Setup:**
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run installer and set a password (remember it!)
3. Open pgAdmin or command prompt
4. Create database: `CREATE DATABASE jobfinder;`
5. Your DATABASE_URL will be:
   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/jobfinder
   ```

**Custom User Setup (Optional):**
```bash
# Create dedicated user
sudo -u postgres psql
CREATE USER jobfinder_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE jobfinder TO jobfinder_user;
\q

# Your DATABASE_URL will be:
DATABASE_URL=postgresql://jobfinder_user:secure_password@localhost:5432/jobfinder
```

### 2. Redis Credentials

**macOS Setup:**
```bash
# Install Redis
brew install redis

# Start Redis
brew services start redis

# Verify it's running
redis-cli ping
# Should return: PONG

# Your REDIS_URL will be:
REDIS_URL=redis://localhost:6379/0
```

**Ubuntu/Linux Setup:**
```bash
# Install Redis
sudo apt-get update
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server

# Enable on boot (optional)
sudo systemctl enable redis-server

# Verify
redis-cli ping

# Your REDIS_URL will be:
REDIS_URL=redis://localhost:6379/0
```

**Windows Setup:**
1. Download Redis from https://github.com/microsoftarchive/redis/releases
2. Extract and run `redis-server.exe`
3. Or use WSL (Windows Subsystem for Linux) and follow Linux instructions

### 3. Generate Security Keys

**Generate SECRET_KEY and JWT_SECRET_KEY:**
```bash
# Generate SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

Copy the output and paste into your `.env` file.

**Example output:**
```
SECRET_KEY=vR3k9Jm2Wp8Qd5Hn7Lz4Cx6Vb1Nt0Ys
JWT_SECRET_KEY=aB4cD8eF2gH6iJ0kL5mN9oP3qR7sT1uV
```

### 4. Adzuna API Credentials (Free - Real Jobs)

**Step-by-step:**
1. Go to https://developer.adzuna.com/
2. Click "Sign Up" in the top right
3. Fill in your details:
   - Email
   - Password
   - Accept terms
4. Verify your email
5. Log in to the developer portal
6. Click "Create Application"
7. Fill in:
   - Application Name: "JobFinder Pro Dev"
   - Description: "Job matching platform for development"
8. Click "Create"
9. Copy your credentials:
   - App ID (looks like: `5af39d52`)
   - App Key (looks like: `7d7832b3b6611ce952d9e8495085b671`)
10. Add to `.env`:
    ```
    ADZUNA_APP_ID=your_app_id_here
    MOCK_CONNECTORS=false
    ```

**Free Tier Limits:**
- 1000 API calls per month
- No credit card required
- Instant activation

### 5. Complete .env File Example

After gathering all credentials, your `.env` should look like:

```env
# Database
DATABASE_URL=postgresql://localhost:5432/jobfinder

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Security (use your generated keys)
SECRET_KEY=vR3k9Jm2Wp8Qd5Hn7Lz4Cx6Vb1Nt0Ys
JWT_SECRET_KEY=aB4cD8eF2gH6iJ0kL5mN9oP3qR7sT1uV
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:3000

# Application
DEBUG=true
DEV_MODE=true
LOG_LEVEL=INFO

# Job Connectors
MOCK_CONNECTORS=false
ADZUNA_APP_ID=5af39d52
INDEED_API_KEY=
JOOBLE_API_KEY=
LINKEDIN_API_KEY=
NAUKRI_API_KEY=

# File Upload
ALLOWED_EXTENSIONS=["pdf", "docx", "txt"]
```

### 6. Verify Your Setup

After setting up `.env`, verify everything works:

```bash
# Check PostgreSQL
pg_isready
# Should return: /tmp:5432 - accepting connections

# Check Redis
redis-cli ping
# Should return: PONG

# Test database connection
python -c "from api.app.core.database import engine; print('Database connected!')"

# Run preflight check
./scripts/preflight_check.sh
```


cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/jobfinder_pro

# Security
SECRET_KEY=your-secret-key-here-change-this-in-production
SESSION_SECRET=your-session-secret-here-change-this-in-production

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys (Optional - uses mock data if not provided)
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_API_KEY=your_adzuna_api_key

# Environment
DEBUG=true
LOG_LEVEL=INFO
```

**Generate secure secret keys:**

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate SESSION_SECRET
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 3.3 Run Database Migrations

```bash
# Apply all migrations to create tables
alembic upgrade head

# Verify tables were created
psql -U postgres -d jobfinder_pro -c "\dt"
```

You should see tables: `users`, `resumes`, `jobs`, `job_matches`, `processing_jobs`, `alembic_version`.

### 4. Frontend Setup

#### 4.1 Install Node.js Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Return to project root
cd ..
```

#### 4.2 Configure Frontend Environment

Create `frontend/.env.local`:

```env
# API URL (points to your local backend)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 4.3 Verify Frontend Installation

```bash
cd frontend
npm run build  # This should complete without errors
cd ..
```

### 5. Redis Setup

#### 5.1 Start Redis Server

**On macOS (using Homebrew):**
```bash
brew services start redis
```

**On Linux:**
```bash
sudo systemctl start redis
# Or
redis-server
```

**On Windows:**
```bash
# Download Redis for Windows or use WSL
redis-server
```

#### 5.2 Verify Redis is Running

```bash
redis-cli ping
# Should return: PONG
```

---

## Running the Application

You need to run three services simultaneously. Use separate terminal windows/tabs for each:

### Terminal 1: Backend API Server

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start FastAPI development server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**What it does:**
- Runs the FastAPI backend on http://localhost:8000
- Auto-reloads on code changes
- Provides API documentation at http://localhost:8000/docs

### Terminal 2: Celery Worker

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start Celery worker
celery -A api.app.celery_app worker --loglevel=info
```

**On Windows:**
```bash
# Celery 5.x doesn't officially support Windows, use this workaround:
celery -A api.app.celery_app worker --loglevel=info --pool=solo
```

**What it does:**
- Processes background tasks (resume parsing, job fetching)
- Handles async job matching
- Monitors Redis for new tasks

### Terminal 3: Frontend Development Server

```bash
# Navigate to frontend directory
cd frontend

# Start Next.js development server
npm run dev
```

**What it does:**
- Runs the Next.js frontend on http://localhost:3000
- Hot-reloads on code changes
- Provides fast refresh for React components

---

## Accessing the Application

Once all services are running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

---

## Environment Variables

### Backend Environment Variables

Create a `.env` file in the project root with these variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `SECRET_KEY` | Yes | - | JWT signing key (use secrets.token_urlsafe(32)) |
| `SESSION_SECRET` | Yes | - | Session encryption key |
| `REDIS_URL` | Yes | `redis://localhost:6379/0` | Redis connection URL |
| `ADZUNA_APP_ID` | No | - | Adzuna API application ID (optional) |
| `ADZUNA_API_KEY` | No | - | Adzuna API key (optional) |
| `DEBUG` | No | `false` | Enable debug mode |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `CORS_ORIGINS` | No | `*` | Allowed CORS origins (comma-separated) |

### Frontend Environment Variables

Create `frontend/.env.local`:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | - | Backend API URL (http://localhost:8000) |

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Error

**Error:** `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution:**
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL if not running
# macOS:
brew services start postgresql@14

# Linux:
sudo systemctl start postgresql

# Windows: Start PostgreSQL service from Services app
```

#### 2. Redis Connection Error

**Error:** `celery.exceptions.ImproperlyConfigured: Cannot connect to redis://localhost:6379/0`

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# Start Redis if not running
# macOS:
brew services start redis

# Linux:
sudo systemctl start redis

# Or manually:
redis-server
```

#### 3. spaCy Model Not Found

**Error:** `OSError: [E050] Can't find model 'en_core_web_sm'`

**Solution:**
```bash
# Download the spaCy English model
python -m spacy download en_core_web_sm

# Verify installation
python -c "import spacy; nlp = spacy.load('en_core_web_sm')"
```

#### 4. Port Already in Use

**Error:** `Address already in use` or `OSError: [Errno 98]` or `EADDRINUSE`

**Solution:**
```bash
# Find and kill process using port 5000 (Frontend)
lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000  # Windows (then taskkill)

# Find and kill process using port 8000 (Backend)
lsof -ti:8000 | xargs kill -9  # macOS/Linux

# Or use different ports:
# Backend:
uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload

# Frontend (edit package.json):
cd frontend
# Change "dev": "next dev -p 5001 -H 0.0.0.0"
npm run dev
```

#### 4a. Missing .env File or JSON Parse Error

**Error:** `error parsing value for field "ALLOWED_EXTENSIONS"` or `.env: No such file or directory` or `JSONDecodeError: Expecting value`

**Solution:**
```bash
# Create .env from example
cp .env.example .env

# If you still get JSON errors, check that ALLOWED_EXTENSIONS in .env is valid JSON:
# Correct format (with spaces after commas):
ALLOWED_EXTENSIONS=["pdf", "docx", "txt"]

# Incorrect format (will cause errors):
ALLOWED_EXTENSIONS=["pdf","docx","txt"]  # Missing spaces
ALLOWED_EXTENSIONS='["pdf", "docx", "txt"]'  # Should not use quotes around the array
```

#### 4b. Invalid ALLOWED_EXTENSIONS Format

**Error:** `json.decoder.JSONDecodeError: Expecting value: line 1 column 2`

**Solution:**
```bash
# Fix ALLOWED_EXTENSIONS in .env file
# Change from: ALLOWED_EXTENSIONS=pdf,docx,txt
# To: ALLOWED_EXTENSIONS=["pdf","docx","txt"]

# Use sed to fix automatically (macOS/Linux)
sed -i.bak 's/ALLOWED_EXTENSIONS=.*/ALLOWED_EXTENSIONS=["pdf","docx","txt"]/' .env

# Or manually edit .env and ensure it's valid JSON array format
```

#### 5. Alembic Migration Errors

**Error:** `alembic.util.exc.CommandError: Target database is not up to date`

**Solution:**
```bash
# Check current migration status
alembic current

# View migration history
alembic history

# Reset and re-run migrations (WARNING: destroys data)
alembic downgrade base
alembic upgrade head

# Or create a new database:
dropdb jobfinder_pro
createdb jobfinder_pro
alembic upgrade head
```

#### 6. Frontend API Connection Issues

**Error:** `Failed to fetch` or CORS errors in browser console

**Solutions:**
- Ensure backend is running on http://localhost:8000
- Check `frontend/.env.local` has correct `NEXT_PUBLIC_API_URL`
- Verify CORS settings in `api/main.py` allow your frontend origin
- Clear browser cache and reload

#### 7. Celery Not Processing Tasks

**Issue:** Tasks are queued but not being processed

**Solutions:**
```bash
# Check if Celery worker is running
# You should see "[INFO/MainProcess] Connected to redis://localhost:6379/0"

# Check Redis queue
redis-cli
> LLEN celery

# Restart Celery worker with verbose logging
celery -A api.app.celery_app worker --loglevel=debug

# On Windows, ensure you use --pool=solo
celery -A api.app.celery_app worker --loglevel=info --pool=solo
```

#### 8. Module Import Errors

**Error:** `ModuleNotFoundError: No module named 'xxx'`

**Solutions:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows

# Reinstall requirements
pip install -r requirements.txt

# For frontend:
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## Development Workflow

### Making Code Changes

1. **Backend changes (Python):**
   - Edit files in `api/` directory
   - Uvicorn auto-reloads (if using `--reload` flag)
   - Check http://localhost:8000/docs for updated API

2. **Frontend changes (TypeScript/React):**
   - Edit files in `frontend/` directory
   - Next.js hot-reloads automatically
   - Check http://localhost:3000 for changes

3. **Database schema changes:**
   ```bash
   # Create new migration
   alembic revision -m "description of change"

   # Edit the generated file in alembic/versions/

   # Apply migration
   alembic upgrade head
   ```

### Running Tests

```bash
# Backend tests
pytest                              # Run all tests
pytest tests/test_matcher.py -v    # Run specific test file
pytest --cov=api --cov-report=html # Run with coverage

# Frontend tests (if configured)
cd frontend
npm test
```

### Code Quality

```bash
# Python linting
pip install black flake8 mypy
black api/                          # Format code
flake8 api/                         # Check style
mypy api/                           # Type checking

# Frontend linting
cd frontend
npm run lint                        # ESLint
```

---

## Database Management

### Create Admin User

```bash
python scripts/cli.py create-admin --email admin@example.com --password SecurePass123
```

### View Database Statistics

```bash
python scripts/cli.py stats
```

### Backup Database

```bash
# Create backup
pg_dump jobfinder_pro > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql jobfinder_pro < backup_20250127_120000.sql
```

### Reset Database

```bash
# WARNING: This deletes all data!
dropdb jobfinder_pro
createdb jobfinder_pro
alembic upgrade head
```

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [spaCy Documentation](https://spacy.io/usage)

---

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [main README.md](README.md) for project overview
2. Review [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
3. Search existing GitHub issues
4. Create a new issue with detailed error messages and steps to reproduce

---

**Last Updated:** October 27, 2025