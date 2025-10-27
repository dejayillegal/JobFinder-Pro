
# JobFinder Pro - Complete Setup Guide

This guide provides step-by-step instructions for setting up JobFinder Pro in different environments.

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Local Deployment (Production-like)](#local-deployment-production-like)
3. [GitHub Actions CI/CD Setup](#github-actions-cicd-setup)
4. [Replit Deployment](#replit-deployment)
5. [Environment Variables Reference](#environment-variables-reference)
6. [Troubleshooting](#troubleshooting)

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
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Security (generate secure random strings)
SECRET_KEY=your-secret-key-here-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-here-min-32-chars
SESSION_SECRET=your-session-secret-here-min-32-chars

# API Keys (optional - uses mock data if not set)
MOCK_CONNECTORS=false
ADZUNA_APP_ID=5af39d52
ADZUNA_API_KEY=7d7832b3b6611ce952d9e8495085b671

# Application
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:5000
DEBUG=true
LOG_LEVEL=INFO
```

**Generate secure secrets:**
```bash
# On Linux/macOS/Windows
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
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
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

1. **Frontend:** http://localhost:5000
2. **API Documentation:** http://localhost:8000/docs
3. **Health Check:** http://localhost:8000/api/health
4. **Metrics:** http://localhost:8000/metrics

### Step 10: Create Test Admin User

```bash
python scripts/cli.py create-admin --email admin@test.com --password admin123
```

---

## Local Deployment (Production-like)

This section covers deploying JobFinder Pro locally in a production-like environment without Docker.

### Prerequisites

All the same prerequisites as development setup, plus:
- **Process manager** (recommended): `supervisord` or `pm2`
- **Reverse proxy** (optional): `nginx` or `caddy`

### Step 1: Production Environment Setup

Create a production `.env` file:

```bash
cp .env.example .env.production
```

Edit `.env.production` with production settings:

```bash
# Database - use production credentials
DATABASE_URL=postgresql://jobfinder_user:secure_password@localhost:5432/jobfinder_prod

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Security - GENERATE NEW SECURE KEYS
SECRET_KEY=<generate-new-32-char-key>
JWT_SECRET_KEY=<generate-new-32-char-key>
SESSION_SECRET=<generate-new-32-char-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://yourdomain.com

# Production settings
DEBUG=false
DEV_MODE=false
LOG_LEVEL=WARNING
ENVIRONMENT=production

# API Keys
MOCK_CONNECTORS=false
ADZUNA_APP_ID=<your-production-key>
ADZUNA_API_KEY=<your-production-key>

# Rate Limiting
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=60
ENABLE_METRICS=true
```

### Step 2: Create Production Database

```bash
# Create production database
createdb jobfinder_prod

# Create database user
psql postgres -c "CREATE USER jobfinder_user WITH PASSWORD 'secure_password';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE jobfinder_prod TO jobfinder_user;"

# Run migrations
export $(cat .env.production | xargs)
alembic upgrade head
```

### Step 3: Build Frontend for Production

```bash
cd frontend
npm run build
cd ..
```

### Step 4: Set Up Process Management with Supervisord

#### Install Supervisord

**On macOS:**
```bash
brew install supervisor
```

**On Ubuntu/Debian:**
```bash
sudo apt-get install supervisor
```

#### Create Supervisor Configuration

Create `/etc/supervisor/conf.d/jobfinder.conf`:

```ini
[program:jobfinder_api]
command=/usr/bin/env bash -c 'source .env.production && uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4'
directory=/path/to/jobfinder-pro
user=youruser
autostart=true
autorestart=true
stderr_logfile=/var/log/jobfinder/api.err.log
stdout_logfile=/var/log/jobfinder/api.out.log
environment=PATH="/usr/local/bin:/usr/bin:/bin"

[program:jobfinder_celery]
command=/usr/bin/env bash -c 'source .env.production && celery -A api.app.celery_app worker --loglevel=info --concurrency=4'
directory=/path/to/jobfinder-pro
user=youruser
autostart=true
autorestart=true
stderr_logfile=/var/log/jobfinder/celery.err.log
stdout_logfile=/var/log/jobfinder/celery.out.log
environment=PATH="/usr/local/bin:/usr/bin:/bin"

[program:jobfinder_frontend]
command=/usr/bin/env bash -c 'cd frontend && npm run start'
directory=/path/to/jobfinder-pro
user=youruser
autostart=true
autorestart=true
stderr_logfile=/var/log/jobfinder/frontend.err.log
stdout_logfile=/var/log/jobfinder/frontend.out.log
environment=PATH="/usr/local/bin:/usr/bin:/bin"
```

#### Create Log Directories

```bash
sudo mkdir -p /var/log/jobfinder
sudo chown youruser:youruser /var/log/jobfinder
```

#### Start Services

```bash
# Reload supervisor configuration
sudo supervisorctl reread
sudo supervisorctl update

# Start all services
sudo supervisorctl start jobfinder_api
sudo supervisorctl start jobfinder_celery
sudo supervisorctl start jobfinder_frontend

# Check status
sudo supervisorctl status
```

### Step 5: Alternative - Process Management with PM2

If you prefer PM2 (especially useful if you're familiar with Node.js):

#### Install PM2

```bash
npm install -g pm2
```

#### Create PM2 Ecosystem File

Create `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [
    {
      name: 'jobfinder-api',
      script: 'uvicorn',
      args: 'api.main:app --host 0.0.0.0 --port 8000 --workers 4',
      interpreter: 'python',
      env_file: '.env.production',
      error_file: './logs/api-error.log',
      out_file: './logs/api-out.log',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G'
    },
    {
      name: 'jobfinder-celery',
      script: 'celery',
      args: '-A api.app.celery_app worker --loglevel=info --concurrency=4',
      interpreter: 'python',
      env_file: '.env.production',
      error_file: './logs/celery-error.log',
      out_file: './logs/celery-out.log',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G'
    },
    {
      name: 'jobfinder-frontend',
      script: 'npm',
      args: 'run start',
      cwd: './frontend',
      error_file: './logs/frontend-error.log',
      out_file: './logs/frontend-out.log',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M'
    }
  ]
};
```

#### Start Services with PM2

```bash
# Create logs directory
mkdir -p logs

# Start all services
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 to start on system boot
pm2 startup

# Monitor services
pm2 monit

# View logs
pm2 logs
```

### Step 6: Set Up Nginx Reverse Proxy (Optional but Recommended)

#### Install Nginx

**On macOS:**
```bash
brew install nginx
```

**On Ubuntu/Debian:**
```bash
sudo apt-get install nginx
```

#### Create Nginx Configuration

Create `/etc/nginx/sites-available/jobfinder`:

```nginx
upstream api_backend {
    server 127.0.0.1:8000;
}

upstream frontend_backend {
    server 127.0.0.1:5000;
}

# HTTP to HTTPS redirect (if using SSL)
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# Main server block
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL configuration (replace with your certificates)
    # ssl_certificate /etc/ssl/certs/yourdomain.crt;
    # ssl_certificate_key /etc/ssl/private/yourdomain.key;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API endpoints
    location /api/ {
        proxy_pass http://api_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Docs endpoints
    location /docs {
        proxy_pass http://api_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Metrics endpoint
    location /metrics {
        proxy_pass http://api_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Frontend
    location / {
        proxy_pass http://frontend_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### Enable and Start Nginx

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/jobfinder /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### Step 7: Set Up SSL with Let's Encrypt (Optional)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is set up automatically
sudo certbot renew --dry-run
```

### Step 8: System Service Management

#### Enable Services on Boot

**For Supervisord:**
```bash
sudo systemctl enable supervisor
```

**For PostgreSQL:**
```bash
sudo systemctl enable postgresql
```

**For Redis:**
```bash
sudo systemctl enable redis-server
```

**For Nginx:**
```bash
sudo systemctl enable nginx
```

### Step 9: Monitoring and Logs

#### View Application Logs

**With Supervisord:**
```bash
# API logs
sudo tail -f /var/log/jobfinder/api.out.log
sudo tail -f /var/log/jobfinder/api.err.log

# Celery logs
sudo tail -f /var/log/jobfinder/celery.out.log

# Frontend logs
sudo tail -f /var/log/jobfinder/frontend.out.log
```

**With PM2:**
```bash
pm2 logs jobfinder-api
pm2 logs jobfinder-celery
pm2 logs jobfinder-frontend
```

#### System Logs

```bash
# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

### Step 10: Database Backup

Create a backup script `/usr/local/bin/backup-jobfinder.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/var/backups/jobfinder"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U jobfinder_user jobfinder_prod | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Keep only last 7 days of backups
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: db_backup_$DATE.sql.gz"
```

Make it executable and set up cron:

```bash
chmod +x /usr/local/bin/backup-jobfinder.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-jobfinder.sh
```

### Step 11: Verify Production Deployment

Run the verification script:

```bash
python scripts/verify_services.py
```

Expected output:
```
✅ Database: Connected
✅ Redis: Connected
✅ API Server: Running on port 8000
✅ Frontend: Running on port 5000

🎉 JobFinder Pro is ready!
   Frontend: http://yourdomain.com
   API Docs: http://yourdomain.com/docs
```

### Step 12: Security Hardening

#### Firewall Configuration

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443

# Enable firewall
sudo ufw enable
```

#### Secure PostgreSQL

Edit `/etc/postgresql/15/main/pg_hba.conf`:

```
# Only allow local connections
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
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
- API Server workflow configured for port 8000

### Step 1: Verify Environment

Check that these secrets are set in Replit Secrets:
- `DATABASE_URL` (auto-configured)
- `SECRET_KEY` (auto-configured)
- `SESSION_SECRET` (auto-configured)
- `REDIS_URL` (optional - defaults to local)
- `ADZUNA_APP_ID` (your API key)
- `ADZUNA_API_KEY` (your API key)

### Step 2: Start Required Services

1. **Start API Server workflow** - Click the dropdown next to Run, select "API Server"
2. **Start Celery Worker workflow** - Click the dropdown, select "Celery Worker"
3. **Frontend is already running** - The Run button starts the Frontend workflow

### Step 3: Verify All Services

Run the verification script in Shell:

```bash
python scripts/verify_services.py
```

### Step 4: Deploy to Production

1. Click the **"Deploy"** button at the top right
2. Select deployment type:
   - **Autoscale** (recommended for production)
   - **Reserved VM** (for consistent performance)
   - **Static** (for frontend-only apps)
3. Configure deployment settings:
   - **Build Command:** `cd frontend && npm run build`
   - **Run Command:** `cd frontend && npm run start`
4. Click **"Deploy your project"**

### Step 5: Access Deployed App

Once deployed, your app will be available at:
- Production URL: `https://<your-repl-name>.<username>.repl.co`
- Custom domain (if configured)

### Step 6: Monitor Deployment

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
| `API_PORT` | API server port | `8000` |

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Error

**Error:** `could not connect to server: Connection refused`

**Solution:**
```bash
# Check if PostgreSQL is running
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
# Find process using port 8000
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
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

#### 7. Supervisord Process Not Starting

**Solution:**
```bash
# Check supervisor logs
sudo tail -f /var/log/supervisor/supervisord.log

# Restart supervisor
sudo systemctl restart supervisor

# Check process status
sudo supervisorctl status
```

#### 8. PM2 Process Crashes

**Solution:**
```bash
# View error logs
pm2 logs jobfinder-api --err

# Restart process
pm2 restart jobfinder-api

# Check process info
pm2 info jobfinder-api
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

### Production (Local Deployment)

```bash
# Using Supervisord
sudo supervisorctl start all
sudo supervisorctl stop all
sudo supervisorctl restart all
sudo supervisorctl status

# Using PM2
pm2 start ecosystem.config.js
pm2 stop all
pm2 restart all
pm2 status
pm2 logs
```

### Database

```bash
# Create admin user
python scripts/cli.py create-admin --email admin@example.com

# View database stats
python scripts/cli.py stats

# Clean old jobs
python scripts/cli.py cleanup-old-jobs --days 30

# Backup database
pg_dump -U jobfinder_user jobfinder_prod > backup.sql

# Restore database
psql -U jobfinder_user jobfinder_prod < backup.sql
```

### System Services

```bash
# Check service status
sudo systemctl status postgresql
sudo systemctl status redis-server
sudo systemctl status nginx
sudo systemctl status supervisor

# Restart services
sudo systemctl restart postgresql
sudo systemctl restart redis-server
sudo systemctl restart nginx
```

---

**Last Updated:** 2025-01-27
**Status:** ✅ Complete setup guide for local development and deployment
