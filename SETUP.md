# JobFinder Pro - Setup Guide

Complete setup instructions for JobFinder Pro on Replit and local environments.

## Table of Contents
1. [Replit Deployment (Recommended)](#replit-deployment-recommended)
2. [Local Development Setup](#local-development-setup)
3. [Environment Variables](#environment-variables)
4. [Troubleshooting](#troubleshooting)

---

## Replit Deployment (Recommended)

JobFinder Pro is optimized for Replit deployment with pre-configured workflows.

### Quick Start

1. **Environment is Pre-configured**: All necessary secrets are in Replit Secrets
2. **Start Services**:
   - Click **Run** button → Starts Frontend (port 5000)
   - Workflow dropdown → Select "Backend API" → Start (port 8000)
   - Workflow dropdown → Select "Celery Worker" → Start (optional)

3. **Access Application**:
   - Frontend: Replit webview
   - API Docs: `https://your-repl.repl.co:8000/docs`

### Deploying to Production

1. **Click "Deploy" Button** in Replit toolbar
2. **Select Deployment Type**: Autoscale (recommended)
3. **Configure Deployment**:
   ```
   Build Command: cd frontend && npm run build
   Run Command: cd frontend && npm run start
   ```
4. **Set Environment Variables**: Already configured in Replit Secrets
5. **Deploy**: Click "Deploy your project"

Your app will be live at `https://your-deployment.repl.co`

### Replit Environment Variables

These are automatically configured in Replit Secrets:

- `DATABASE_URL`: PostgreSQL connection (auto-configured)
- `SECRET_KEY`: JWT signing key (auto-generated)
- `JWT_SECRET_KEY`: Auth key (auto-generated)
- `REDIS_URL`: Redis connection (defaults to local Redis)
- `ADZUNA_APP_ID`: (optional) Your Adzuna API ID
- `ADZUNA_API_KEY`: (optional) Your Adzuna API key

### Adding Real Job Data

To fetch real jobs instead of mock data:

1. **Get Adzuna API Credentials** (FREE):
   - Visit https://developer.adzuna.com/
   - Sign up and create an application
   - Copy App ID and API Key

2. **Add to Replit Secrets**:
   - Open Secrets tab (🔒 icon)
   - Add `ADZUNA_APP_ID` with your app id
   - Add `ADZUNA_API_KEY` with your api key

3. **Restart Backend API Workflow**

---

## Local Development Setup

### Prerequisites

Install the following:

- **Python 3.11+**: [Download](https://www.python.org/downloads/)
- **Node.js 18+**: [Download](https://nodejs.org/)
- **PostgreSQL 15+**: [Download](https://www.postgresql.org/download/)
- **Redis 7+**: [Download](https://redis.io/download/)
- **Git**: [Download](https://git-scm.com/downloads/)

### Automated Setup

```bash
# 1. Clone repository
git clone <your-repo-url>
cd jobfinder-pro

# 2. Run automated setup
chmod +x scripts/local_setup.sh
./scripts/local_setup.sh

# This script will:
# - Create .env file from template
# - Install Python dependencies
# - Download spaCy model
# - Create PostgreSQL database
# - Run database migrations
# - Install frontend dependencies
# - Generate secure keys
```

### Manual Setup

If the automated script fails, follow these steps:

#### 1. Environment Configuration

```bash
# Copy template
cp .env.example .env

# Generate secure keys
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"

# Add these to .env file
```

#### 2. Database Setup

```bash
# Create database
createdb jobfinder

# Verify connection
psql jobfinder -c "SELECT version();"
```

#### 3. Python Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Verify installation
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✓ spaCy OK')"
```

#### 4. Database Migrations

```bash
# Run migrations
alembic upgrade head

# Verify tables
psql jobfinder -c "\dt"
# Should show: users, resumes, jobs, job_matches, processing_jobs
```

#### 5. Frontend Setup

```bash
# Install Node dependencies
cd frontend
npm install
cd ..
```

#### 6. Redis Setup

```bash
# Start Redis
# macOS:
brew services start redis

# Linux:
sudo systemctl start redis-server

# Verify
redis-cli ping  # Should return: PONG
```

### Starting Services

You need 3 terminal windows:

**Terminal 1 - Backend API:**
```bash
chmod +x scripts/start_backend.sh
./scripts/start_backend.sh

# Or manually:
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Celery Worker:**
```bash
chmod +x scripts/start_celery.sh
./scripts/start_celery.sh

# Or manually:
celery -A api.app.celery_app worker --loglevel=info
```

**Terminal 3 - Frontend:**
```bash
chmod +x scripts/start_frontend.sh
./scripts/start_frontend.sh

# Or manually:
cd frontend && npm run dev -- -p 5000
```

### Access Points

- Frontend: http://localhost:5000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://localhost:5432/jobfinder` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT signing key | Generate with `secrets.token_urlsafe(32)` |
| `JWT_SECRET_KEY` | Auth key | Generate with `secrets.token_urlsafe(32)` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ADZUNA_APP_ID` | Adzuna API app id | Uses mock data |
| `ADZUNA_API_KEY` | Adzuna API key | Uses mock data |
| `STORE_RESUME_RAW` | Store raw resume text | `false` (GDPR) |
| `ANONYMIZE_JOBS` | Anonymize job data | `true` |
| `EMBEDDING_BACKEND` | Matching algorithm | `tfidf` |
| `DEBUG` | Debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

See [.env.example](.env.example) for complete list.

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Find and kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

#### 2. Database Connection Error

```bash
# Check PostgreSQL is running
pg_isready

# Start PostgreSQL
brew services start postgresql@15  # macOS
sudo systemctl start postgresql    # Linux

# Verify DATABASE_URL in .env
echo $DATABASE_URL
```

#### 3. Redis Connection Error

```bash
# Check Redis is running
redis-cli ping  # Should return PONG

# Start Redis
brew services start redis          # macOS
sudo systemctl start redis-server  # Linux
```

#### 4. spaCy Model Not Found

```bash
# Download model
python -m spacy download en_core_web_sm

# Verify
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('OK')"
```

#### 5. Module Not Found Errors

```bash
# Reinstall Python dependencies
pip install -r requirements.txt

# Reinstall frontend dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### 6. Celery Not Processing Tasks

```bash
# Check Redis connection
redis-cli ping

# Restart Celery worker
# Kill existing worker, then:
celery -A api.app.celery_app worker --loglevel=info
```

### Validation Script

Run this to check your setup:

```bash
python tests/validate_setup.py
```

Expected output:
```
✓ Database: Connected
✓ Redis: Connected
✓ spaCy: Model loaded
✓ Environment: Configured
✓ All systems ready!
```

---

## Next Steps

1. **Local Development**: See [SETUP_LOCAL.md](SETUP_LOCAL.md) for detailed local setup
2. **Quick Start**: See [QUICK_START.md](QUICK_START.md) for 5-minute setup
3. **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
4. **Privacy**: See [PRIVACY_AND_GDPR.md](PRIVACY_AND_GDPR.md) for privacy features

---

**Need Help?**

- Run validation: `python tests/validate_setup.py`
- Check logs in terminal windows
- Review error messages in console
- Consult troubleshooting section above

**Last Updated**: January 27, 2025