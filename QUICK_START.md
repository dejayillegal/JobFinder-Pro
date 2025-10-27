# Quick Start Guide for JobFinder Pro

This is a rapid-fire guide to get you up and running in under 10 minutes.

## 1-Minute Overview

JobFinder Pro is an AI-powered job matching platform that:
- Parses your resume (PDF/DOCX/TXT)
- Matches you with relevant jobs from multiple sources
- Uses explainable AI scoring (Skills 60%, Seniority 25%, Location 15%)
- Focuses on India-based jobs with Bangalore/Remote priority

## Prerequisites Install

Install these first (skip if already installed):

```bash
# macOS
brew install python@3.11 node postgresql redis

# Ubuntu/Debian
sudo apt install python3.11 python3.11-venv nodejs npm postgresql redis-server

# Windows (using Chocolatey)
choco install python nodejs postgresql redis
```

## 5-Minute Setup

```bash
# 1. Clone
git clone <your-repo-url>
cd jobfinder-pro

# 2. Backend (Python)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Database
createdb jobfinder_pro
cp .env.example .env
# Edit .env with your DATABASE_URL and SECRET_KEY
alembic upgrade head

# 4. Frontend (Node.js)
cd frontend && npm install && cd ..

# 5. Start Redis (if not auto-started)
redis-server  # Or: brew services start redis
```

## Run the App

Open 3 terminal windows:

**Terminal 1 - API:**
```bash
source venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Worker:**
```bash
source venv/bin/activate
celery -A api.app.celery_app worker --loglevel=info
# Windows: add --pool=solo flag
```

**Terminal 3 - Frontend:**
```bash
cd frontend && npm run dev
```

## Access

- 🌐 **Frontend**: http://localhost:3000
- 📚 **API Docs**: http://localhost:8000/docs
- ❤️ **Health**: http://localhost:8000/health

## First Steps

1. Visit http://localhost:3000
2. Click "Register" to create an account
3. Upload your resume (PDF, DOCX, or TXT)
4. Wait ~30 seconds for processing
5. View your job matches!

## Troubleshooting

**Port in use?**
```bash
# Kill process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

**Database error?**
```bash
# Check PostgreSQL is running
pg_isready

# Recreate database
dropdb jobfinder_pro && createdb jobfinder_pro
alembic upgrade head
```

**Redis error?**
```bash
# Check Redis is running
redis-cli ping  # Should return PONG

# Start Redis
brew services start redis  # macOS
sudo systemctl start redis  # Linux
```

## What's Next?

- **Detailed Setup**: See [SETUP_LOCAL.md](SETUP_LOCAL.md) for comprehensive instructions
- **Production Deploy**: See [SETUP.md](SETUP.md) for Docker/Kubernetes deployment
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- **API Reference**: Visit http://localhost:8000/docs after starting the backend

## Configuration

Generate secure keys for `.env`:
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('SESSION_SECRET=' + secrets.token_urlsafe(32))"
```

Minimal `.env` file:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/jobfinder_pro
SECRET_KEY=your-generated-secret-key-here
SESSION_SECRET=your-generated-session-secret-here
REDIS_URL=redis://localhost:6379/0
DEBUG=true
```

## Architecture Summary

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Next.js   │  HTTP   │   FastAPI   │  Tasks  │   Celery    │
│  Frontend   ├────────>│   Backend   ├────────>│   Worker    │
│  (Port 3000)│         │  (Port 8000)│         │  (Redis)    │
└─────────────┘         └──────┬──────┘         └─────────────┘
                               │
                               v
                        ┌─────────────┐
                        │ PostgreSQL  │
                        │  Database   │
                        └─────────────┘
```

## Help & Support

- 📖 Check [SETUP_LOCAL.md](SETUP_LOCAL.md) for detailed troubleshooting
- 🐛 Found a bug? Open an issue on GitHub
- 💡 Have questions? Check existing issues or create a new one

---

**Ready to dive deeper?** Read [SETUP_LOCAL.md](SETUP_LOCAL.md) for comprehensive setup instructions.
