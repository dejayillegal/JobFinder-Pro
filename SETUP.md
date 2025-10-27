
# JobFinder Pro - Complete Setup Guide

This guide provides step-by-step instructions for setting up JobFinder Pro in different environments.

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [GitHub Actions CI/CD Setup](#github-actions-cicd-setup)
3. [Replit Deployment](#replit-deployment)
4. [Environment Variables Reference](#environment-variables-reference)
5. [Troubleshooting](#troubleshooting)

---

## Local Development Setup

### Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **PostgreSQL 15+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **Redis 7+** - [Download Redis](https://redis.io/download/)
- **Git** - [Download Git](https://git-scm.com/downloads/)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/jobfinder-pro.git
cd jobfinder-pro
```

### Step 2: Set Up PostgreSQL Database

#### On macOS (using Homebrew):
```bash
brew install postgresql@15
brew services start postgresql@15
createdb jobfinder
```

#### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb jobfinder
sudo -u postgres createuser -s $USER
```

#### On Windows:
1. Download and install PostgreSQL from the official website
2. Use pgAdmin or command line to create database:
```sql
CREATE DATABASE jobfinder;
```

### Step 3: Set Up Redis

#### On macOS:
```bash
brew install redis
brew services start redis
```

#### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
```

#### On Windows:
1. Download Redis from [Redis Windows port](https://github.com/microsoftarchive/redis/releases)
2. Extract and run `redis-server.exe`

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Database
DATABASE_URL=postgresql://localhost:5432/jobfinder

# Redis
REDIS_URL=redis://localhost:6379/0

# Security (generate secure random strings)
SECRET_KEY=your-secret-key-here-min-32-chars
SESSION_SECRET=your-session-secret-here-min-32-chars

# API Keys (optional - uses mock data if not set)
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_API_KEY=your-adzuna-api-key

# Application
DEBUG=true
LOG_LEVEL=INFO
```

**Generate secure secrets:**
```bash
# On Linux/macOS
python -c "import secrets; print(secrets.token_urlsafe(32))"

# On Windows (PowerShell)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 5: Install Python Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

### Step 6: Run Database Migrations

```bash
# Apply all migrations
alembic upgrade head

# Verify tables were created
python -c "from api.app.core.database import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())"
```

### Step 7: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### Step 8: Start All Services

#### Option A: Using the Startup Script (Recommended)

```bash
chmod +x scripts/dev_start.sh
./scripts/dev_start.sh
```

#### Option B: Manual Start (separate terminals)

**Terminal 1 - API Server:**
```bash
uvicorn api.main:app --host 0.0.0.0 --port 5000 --reload
```

**Terminal 2 - Celery Worker:**
```bash
celery -A api.app.celery_app worker --loglevel=info
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 9: Verify Installation

1. **Frontend:** http://localhost:3000
2. **API Documentation:** http://localhost:5000/docs
3. **Health Check:** http://localhost:5000/health
4. **Metrics:** http://localhost:5000/metrics

### Step 10: Create Test Admin User

```bash
python scripts/cli.py create-admin --email admin@test.com --password admin123
```

---

## GitHub Actions CI/CD Setup

### Step 1: Create GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

```
DATABASE_URL: postgresql://postgres:postgres@localhost:5432/jobfinder_test
REDIS_URL: redis://localhost:6379/0
SECRET_KEY: <generate-secure-random-string>
SESSION_SECRET: <generate-secure-random-string>
ADZUNA_APP_ID: <optional>
ADZUNA_API_KEY: <optional>
```

### Step 2: Create GitHub Actions Workflow

The workflow file is already included in the project. Here's what it does:

**File:** `.github/workflows/ci.yml` (already exists in project)

- Runs on every push and pull request
- Sets up Python 3.11 and Node.js 18
- Installs PostgreSQL and Redis
- Runs database migrations
- Executes Python tests with coverage
- Runs linting checks
- Tests frontend build

### Step 3: View CI/CD Results

After pushing to GitHub:

1. Go to the **Actions** tab in your repository
2. Click on the latest workflow run
3. View logs for each job (test, lint, build)

---

## Replit Deployment

### Current Setup

Your Replit is already configured with:
- PostgreSQL database (integrated)
- Environment secrets (managed by Replit)
- Frontend workflow running on port 5000

### Step 1: Verify Environment

Check that these secrets are set in Replit Secrets:
- `DATABASE_URL` (auto-configured)
- `SECRET_KEY` (auto-configured)
- `SESSION_SECRET` (auto-configured)
- `REDIS_URL` (optional - defaults to local)

### Step 2: Deploy to Production

1. Click the **"Release"** button at the top right
2. Select **"Deploy"** option
3. Choose your deployment tier (Shared or Dedicated)
4. Configure deployment settings:
   - **Build Command:** `cd frontend && npm run build`
   - **Run Command:** `cd frontend && npm run start`
5. Click **"Deploy your project"**

### Step 3: Access Deployed App

Once deployed, your app will be available at:
- Production URL: `https://<your-repl-name>.<username>.repl.co`
- Custom domain (if configured)

### Step 4: Monitor Deployment

View deployment status and logs:
1. Click on the deployment in the Deployments panel
2. View build logs and runtime logs
3. Check metrics at `/metrics` endpoint

---

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/dbname` |
| `SECRET_KEY` | JWT signing key (min 32 chars) | `<random-string>` |
| `SESSION_SECRET` | Session encryption key | `<random-string>` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `ADZUNA_APP_ID` | Adzuna API application ID | Uses mock data |
| `ADZUNA_API_KEY` | Adzuna API key | Uses mock data |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Error

**Error:** `could not connect to server: Connection refused`

**Solution:**
```bash
# Check if PostgreSQL is running
# macOS/Linux
pg_isready

# Start PostgreSQL if not running
# macOS
brew services start postgresql@15

# Linux
sudo systemctl start postgresql
```

#### 2. Redis Connection Error

**Error:** `Error connecting to Redis`

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# Should return: PONG

# Start Redis if not running
# macOS
brew services start redis

# Linux
sudo systemctl start redis-server
```

#### 3. Module Not Found Error

**Error:** `ModuleNotFoundError: No module named 'spacy'`

**Solution:**
```bash
# Reinstall all dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

#### 4. Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 5000
# macOS/Linux
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

#### 5. Database Migration Fails

**Error:** `Target database is not up to date`

**Solution:**
```bash
# Reset migrations (WARNING: drops all data)
alembic downgrade base
alembic upgrade head

# Or create new migration
alembic revision --autogenerate -m "fix schema"
alembic upgrade head
```

#### 6. Frontend Build Fails

**Error:** `npm ERR! code ELIFECYCLE`

**Solution:**
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Getting Help

If you encounter issues not covered here:

1. Check the [README.md](README.md) for additional documentation
2. Review [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
3. Check existing GitHub issues
4. Create a new issue with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Python version, Node version)

---

## Quick Reference Commands

### Development

```bash
# Start development environment
make dev

# Run tests
make test

# Run linting
make lint

# Format code
make format

# Create database migration
make migrate-create

# Apply migrations
make migrate
```

### Database

```bash
# Create admin user
python scripts/cli.py create-admin --email admin@example.com

# View database stats
python scripts/cli.py stats

# Clean old jobs
python scripts/cli.py cleanup-old-jobs --days 30
```

### Docker (Optional - for local testing)

```bash
# Build images
make docker-build

# Start all services
make docker-up

# Stop services
make docker-down

# View logs
make docker-logs
```

---

**Last Updated:** 2025-10-27
**Status:** ✅ Complete setup guide for local and CI/CD
