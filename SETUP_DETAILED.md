
# JobFinder Pro - Detailed Setup Instructions

This guide provides step-by-step instructions for configuring all environment variables and services.

## Table of Contents
1. [Database Configuration](#database-configuration)
2. [Redis Configuration](#redis-configuration)
3. [Security Configuration](#security-configuration)
4. [API Keys Configuration](#api-keys-configuration)
5. [Celery Configuration](#celery-configuration)
6. [Complete Setup Workflow](#complete-setup-workflow)

---

## Database Configuration

### PostgreSQL Setup

**Option 1: Local PostgreSQL (Development)**

1. **Install PostgreSQL 15+**

   **macOS:**
   ```bash
   brew install postgresql@15
   brew services start postgresql@15
   ```

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install postgresql postgresql-contrib
   sudo systemctl start postgresql
   ```

   **Windows:**
   - Download from [postgresql.org](https://www.postgresql.org/download/)
   - Run installer and note down password

2. **Create Database**

   ```bash
   # macOS/Linux
   createdb jobfinder
   
   # Or use psql
   psql postgres
   CREATE DATABASE jobfinder;
   \q
   ```

3. **Set DATABASE_URL in .env**

   ```bash
   # Format: postgresql://username:password@host:port/database
   DATABASE_URL=postgresql://localhost:5432/jobfinder
   
   # With credentials
   DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/jobfinder
   ```

**Option 2: Replit PostgreSQL (Production)**

On Replit, PostgreSQL is automatically configured:
- DATABASE_URL is set in Replit Secrets
- No manual setup required
- Database is managed by Replit

---

## Redis Configuration

### Redis Setup for Celery

Redis is required for background job processing via Celery.

**Option 1: Local Redis (Development)**

1. **Install Redis 7+**

   **macOS:**
   ```bash
   brew install redis
   brew services start redis
   ```

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install redis-server
   sudo systemctl start redis-server
   sudo systemctl enable redis-server
   ```

   **Windows:**
   - Download from [Redis Windows](https://github.com/microsoftarchive/redis/releases)
   - Extract and run `redis-server.exe`

2. **Verify Redis is Running**

   ```bash
   redis-cli ping
   # Should return: PONG
   ```

3. **Set Redis URLs in .env**

   ```bash
   REDIS_URL=redis://localhost:6379/0
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/1
   ```

**Option 2: Replit Redis**

For Replit deployments:
```bash
# Replit's local Redis (if available)
REDIS_URL=redis://localhost:6379/0

# Or use an external Redis service:
# - Upstash Redis (https://upstash.com/)
# - Redis Labs (https://redis.com/)
REDIS_URL=redis://username:password@hostname:port/0
```

---

## Security Configuration

### Generate Secure Keys

**CRITICAL:** Never use default keys in production!

1. **Generate SECRET_KEY**

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Generate JWT_SECRET_KEY**

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Generate SESSION_SECRET**

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. **Add to .env file**

   ```bash
   SECRET_KEY=abc123XYZ789_your_generated_key_here_32chars
   JWT_SECRET_KEY=def456UVW012_your_generated_jwt_key_here
   SESSION_SECRET=ghi789RST345_your_generated_session_key
   
   # JWT Configuration
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
   ```

**Security Best Practices:**
- Use different keys for each environment (dev, staging, prod)
- Store production keys in Replit Secrets (not in .env file)
- Rotate keys periodically
- Never commit secrets to Git

---

## API Keys Configuration

### Adzuna API (Real Job Data)

**Adzuna** is the only connector with full API integration.

1. **Sign up for Adzuna Developer Account**
   - Go to https://developer.adzuna.com/
   - Create account
   - Create new application

2. **Get API Credentials**
   - App ID: Found in dashboard
   - API Key: Found in dashboard

3. **Add to .env**

   ```bash
   MOCK_CONNECTORS=false
   ADZUNA_APP_ID=5af39d52
   ADZUNA_API_KEY=7d7832b3b6611ce952d9e8495085b671
   ```

### Other Connectors (Mock Data Only)

For legal and Terms of Service compliance, other connectors use mock data:

```bash
# These should remain EMPTY to use mock data
INDEED_API_KEY=
JOOBLE_API_KEY=
LINKEDIN_API_KEY=
NAUKRI_API_KEY=
```

**Why Mock Data?**
- **Indeed**: Requires official partnership
- **LinkedIn**: Web scraping violates Terms of Service
- **Jooble**: API access requires business agreement
- **Naukri**: robots.txt restrictions

**Mock data provides:**
- Realistic job listings for testing
- No API rate limits
- Consistent test results
- No legal concerns

---

## Celery Configuration

### Background Task Processing

Celery handles asynchronous tasks like resume parsing and job matching.

1. **Ensure Redis is Running** (see Redis Configuration above)

2. **Set Celery URLs in .env**

   ```bash
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/1
   ```

   **Note:** We use different Redis databases (0 and 1) for separation.

3. **Start Celery Worker** (in separate terminal)

   ```bash
   celery -A api.app.celery_app worker --loglevel=info
   ```

4. **Verify Celery is Working**

   Check terminal output for:
   ```
   [INFO/MainProcess] Connected to redis://localhost:6379/0
   [INFO/MainProcess] celery@hostname ready.
   ```

---

## Complete Setup Workflow

### Step-by-Step Setup

1. **Clone Repository**

   ```bash
   git clone https://github.com/yourusername/jobfinder-pro.git
   cd jobfinder-pro
   ```

2. **Install System Dependencies**

   ```bash
   # PostgreSQL
   brew install postgresql@15  # macOS
   # sudo apt-get install postgresql  # Linux
   
   # Redis
   brew install redis  # macOS
   # sudo apt-get install redis-server  # Linux
   ```

3. **Start Services**

   ```bash
   # PostgreSQL
   brew services start postgresql@15  # macOS
   # sudo systemctl start postgresql  # Linux
   
   # Redis
   brew services start redis  # macOS
   # sudo systemctl start redis-server  # Linux
   ```

4. **Create Database**

   ```bash
   createdb jobfinder
   ```

5. **Create .env File**

   ```bash
   cp .env.example .env
   ```

6. **Generate Security Keys**

   ```bash
   echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env
   echo "JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env
   echo "SESSION_SECRET=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env
   ```

7. **Edit .env with Your Values**

   ```bash
   # Database
   DATABASE_URL=postgresql://localhost:5432/jobfinder
   
   # Redis
   REDIS_URL=redis://localhost:6379/0
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/1
   
   # Security (already generated in step 6)
   # SECRET_KEY=...
   # JWT_SECRET_KEY=...
   # SESSION_SECRET=...
   
   # Adzuna API
   MOCK_CONNECTORS=false
   ADZUNA_APP_ID=5af39d52
   ADZUNA_API_KEY=7d7832b3b6611ce952d9e8495085b671
   
   # Other APIs (leave empty for mock data)
   INDEED_API_KEY=
   JOOBLE_API_KEY=
   LINKEDIN_API_KEY=
   NAUKRI_API_KEY=
   ```

8. **Install Python Dependencies**

   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

9. **Run Database Migrations**

   ```bash
   alembic upgrade head
   ```

10. **Install Frontend Dependencies**

    ```bash
    cd frontend
    npm install
    cd ..
    ```

11. **Start All Services**

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

12. **Verify Setup**

    - Frontend: http://localhost:3000
    - API Docs: http://localhost:5000/docs
    - Health Check: http://localhost:5000/health

---

## Environment Variables Reference

### Complete .env Template

```bash
# DATABASE CONFIGURATION
DATABASE_URL=postgresql://localhost:5432/jobfinder

# REDIS CONFIGURATION
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# SECURITY CONFIGURATION
SECRET_KEY=your-generated-secret-key-here
JWT_SECRET_KEY=your-generated-jwt-secret-key-here
SESSION_SECRET=your-generated-session-secret-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API KEYS
MOCK_CONNECTORS=false
ADZUNA_APP_ID=5af39d52
ADZUNA_API_KEY=7d7832b3b6611ce952d9e8495085b671
INDEED_API_KEY=
JOOBLE_API_KEY=
LINKEDIN_API_KEY=
NAUKRI_API_KEY=

# APPLICATION
API_HOST=0.0.0.0
API_PORT=5000
FRONTEND_URL=http://localhost:3000
DEBUG=true
DEV_MODE=true
LOG_LEVEL=INFO
ENVIRONMENT=development

# RESUME PROCESSING
MAX_FILE_SIZE_MB=10
ALLOWED_EXTENSIONS=pdf,docx,txt
SPACY_MODEL=en_core_web_sm
USE_EMBEDDINGS=false

# JOB MATCHING
DEFAULT_COUNTRY=India
PRIORITY_LOCATIONS=Bangalore,Remote
MIN_MATCH_SCORE=50
MAX_MATCHES=50
JOB_REFRESH_INTERVAL=24

# RATE LIMITING & MONITORING
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=60
ENABLE_METRICS=true

# FILE STORAGE
UPLOAD_DIR=./uploads
```

---

## Troubleshooting

### Database Issues

**Error: "could not connect to server"**
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL
brew services start postgresql@15  # macOS
sudo systemctl start postgresql  # Linux
```

### Redis Issues

**Error: "Error connecting to Redis"**
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
brew services start redis  # macOS
sudo systemctl start redis-server  # Linux
```

### Celery Issues

**Error: "Celery not connecting"**
- Ensure Redis is running
- Check CELERY_BROKER_URL matches REDIS_URL
- Verify firewall isn't blocking port 6379

### API Key Issues

**Error: "Adzuna API authentication failed"**
- Verify ADZUNA_APP_ID and ADZUNA_API_KEY are correct
- Check API quota hasn't been exceeded
- Set MOCK_CONNECTORS=true as fallback

---

**Last Updated:** 2025-01-27
