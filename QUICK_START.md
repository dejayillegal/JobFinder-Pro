
# Quick Start Guide for JobFinder Pro

Get JobFinder Pro running in under 10 minutes!

## 1-Minute Overview

JobFinder Pro is an AI-powered job matching platform that:
- Parses your resume (PDF/DOCX/TXT)
- Matches you with relevant jobs using TF-IDF algorithm
- Aggregates jobs from Adzuna API and RSS feeds
- Focuses on India-based jobs with Bangalore/Remote priority
- Provides explainable matching scores

## Replit Deployment (Fastest - 2 Minutes)

**Already on Replit? You're almost done!**

1. **Check Environment**: Replit Secrets are pre-configured
2. **Start Services**:
   - Click **Run** button (starts Frontend on port 5000)
   - Open workflow dropdown, select "Backend API" and start
   - (Optional) Start "Celery Worker" for background jobs
3. **Access Application**: Use Replit's webview or your deployment URL
4. **Create Account**: Register at `/register` and upload your resume!

**That's it!** The app is running with mock job data by default.

### Optional: Get Real Jobs (Adzuna API)

1. Sign up at https://developer.adzuna.com/ (free, no credit card)
2. Create an application and get your App ID and API Key
3. Add to Replit Secrets:
   - `ADZUNA_APP_ID`: your app id
   - `ADZUNA_API_KEY`: your api key
4. Restart Backend API workflow

## Local Setup (5 Minutes)

### Prerequisites

Install these first:

```bash
# macOS
brew install python@3.11 node postgresql redis

# Ubuntu/Debian
sudo apt install python3.11 nodejs npm postgresql redis-server

# Verify installations
python3 --version  # Should be 3.11+
node --version     # Should be 18+
psql --version     # Should be 15+
redis-cli --version # Should be 7+
```

### Automated Setup

```bash
# 1. Clone repository
git clone <your-repo-url>
cd jobfinder-pro

# 2. Run setup script
chmod +x scripts/local_setup.sh
./scripts/local_setup.sh

# Script will:
# - Create .env file
# - Install Python dependencies
# - Download spaCy model
# - Create database
# - Install frontend dependencies
# - Run migrations

# 3. Start services (3 terminals)

# Terminal 1 - Backend API
chmod +x scripts/start_backend.sh
./scripts/start_backend.sh

# Terminal 2 - Celery Worker  
chmod +x scripts/start_celery.sh
./scripts/start_celery.sh

# Terminal 3 - Frontend
chmod +x scripts/start_frontend.sh
./scripts/start_frontend.sh
```

### Manual Setup (If Scripts Fail)

```bash
# 1. Environment
cp .env.example .env
# Generate secrets:
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
# Add these to .env

# 2. Database
createdb jobfinder

# 3. Python dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 4. Migrations
alembic upgrade head

# 5. Frontend
cd frontend && npm install && cd ..

# 6. Start services (3 terminals)
# Terminal 1:
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2:
celery -A api.app.celery_app worker --loglevel=info

# Terminal 3:
cd frontend && npm run dev -- -p 5000
```

## Access Points

Once running:

- **Frontend**: http://localhost:5000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

## First Steps

1. **Register**: Go to http://localhost:5000/register
2. **Upload Resume**: Navigate to `/upload` and upload your resume (PDF/DOCX/TXT)
3. **Wait**: Processing takes ~30 seconds
4. **View Matches**: Check `/matches` for your personalized job recommendations!

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### Database Connection Failed

```bash
# Check PostgreSQL is running
pg_isready

# Start PostgreSQL
brew services start postgresql@15  # macOS
sudo systemctl start postgresql    # Linux

# Recreate database
dropdb jobfinder && createdb jobfinder
alembic upgrade head
```

### Redis Connection Failed

```bash
# Check Redis
redis-cli ping  # Should return PONG

# Start Redis
brew services start redis          # macOS
sudo systemctl start redis-server  # Linux
```

### spaCy Model Not Found

```bash
# Reinstall spaCy model
python -m spacy download en_core_web_sm

# Verify
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('OK')"
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# For frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Architecture Overview

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Next.js   │  HTTP   │   FastAPI   │  Tasks  │   Celery    │
│  Frontend   ├────────>│   Backend   ├────────>│   Worker    │
│  (Port 5000)│         │  (Port 8000)│         │  (Redis)    │
└─────────────┘         └──────┬──────┘         └─────────────┘
                               │
                               v
                        ┌─────────────┐
                        │ PostgreSQL  │
                        │  Database   │
                        └─────────────┘
```

## Configuration Quick Reference

Minimal `.env` file:

```bash
# Database
DATABASE_URL=postgresql://localhost:5432/jobfinder

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Security (generate these!)
SECRET_KEY=<run: python -c "import secrets; print(secrets.token_urlsafe(32))">
JWT_SECRET_KEY=<run same command again>

# Optional - Adzuna for real jobs
ADZUNA_APP_ID=your_app_id
ADZUNA_API_KEY=your_api_key

# Privacy
STORE_RESUME_RAW=false
ANONYMIZE_JOBS=true
```

## What's Next?

- **Detailed Setup**: See [SETUP_LOCAL.md](SETUP_LOCAL.md) for comprehensive local setup
- **Production Deploy**: See [SETUP.md](SETUP.md) for Replit deployment guide
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- **API Reference**: Visit http://localhost:8000/docs after starting backend

## Getting Help

1. Check [SETUP_LOCAL.md](SETUP_LOCAL.md) for detailed troubleshooting
2. Run validation: `python tests/validate_setup.py`
3. Check logs in respective terminal windows
4. Review GitHub issues for known problems

---

**Ready?** Start with automated setup or jump to detailed guides above!
