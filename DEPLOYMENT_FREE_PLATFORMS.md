# Deployment Guide for Free Platforms

This guide shows you how to deploy JobFinder Pro using completely free hosting platforms. No credit card required for most services!

## Table of Contents
- [Overview](#overview)
- [Backend Deployment Options](#backend-deployment-options)
  - [Option 1: Render (Recommended)](#option-1-render-recommended)
  - [Option 2: Railway](#option-2-railway)
  - [Option 3: Fl0](#option-3-fl0)
- [Frontend Deployment](#frontend-deployment)
- [Database Options](#database-options)
- [Redis/Cache Options](#rediscache-options)
- [Complete Free Stack](#complete-free-stack)

---

## Overview

**Recommended Free Stack:**
- **Backend**: Render (Free tier - 750 hours/month)
- **Frontend**: Vercel (Unlimited free)
- **Database**: Neon Postgres (Free tier - 512MB)
- **Redis**: Upstash (Free tier - 10K commands/day)

**Total Cost**: $0/month with generous free tiers

---

## Backend Deployment Options

### Option 1: Render (Recommended)

Render offers 750 free hours per month for web services.

#### Step 1: Create Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (recommended) or email

#### Step 2: Deploy Backend

```bash
# 1. Push your code to GitHub
git add .
git commit -m "Prepare for deployment"
git push origin main

# 2. In Render Dashboard:
#    - Click "New +" → "Web Service"
#    - Connect your GitHub repository
#    - Configure:

Name: jobfinder-pro-api
Environment: Python 3
Build Command: pip install -r requirements.txt && python -m spacy download en_core_web_sm
Start Command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
Instance Type: Free
```

#### Step 3: Add Environment Variables

In Render dashboard, add these environment variables:

```env
DATABASE_URL=<your-neon-postgres-url>
REDIS_URL=<your-upstash-redis-url>
SECRET_KEY=<generate-with-python-secrets>
JWT_SECRET_KEY=<generate-with-python-secrets>
SESSION_SECRET=<generate-with-python-secrets>
ADZUNA_APP_ID=<optional>
ADZUNA_API_KEY=<optional>
```

Generate secrets:
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('SESSION_SECRET=' + secrets.token_urlsafe(32))"
```

#### Step 4: Deploy

Click "Create Web Service" and wait for deployment (5-10 minutes).

**Your backend will be available at**: `https://jobfinder-pro-api.onrender.com`

---

### Option 2: Railway

Railway offers $5 free credits per month (enough for small projects).

#### Step 1: Setup

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init
```

#### Step 2: Deploy

```bash
# Deploy backend
railway up

# Add environment variables
railway variables set DATABASE_URL=<postgres-url>
railway variables set REDIS_URL=<redis-url>
railway variables set SECRET_KEY=<your-secret>
```

#### Step 3: Create Services

In Railway Dashboard:
1. Add PostgreSQL database (automatically provisions)
2. Add Redis (automatically provisions)
3. Link services to your web service

**Your backend will be available at**: `https://your-project.up.railway.app`

---

### Option 3: Fl0

Fl0 offers free hosting for Python/Node.js applications.

#### Step 1: Deploy

1. Visit [fl0.com](https://fl0.com)
2. Connect GitHub repository
3. Fl0 auto-detects Python and configures
4. Add environment variables in dashboard

**Start Command**:
```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

---

## Frontend Deployment

### Vercel (Recommended - Free & Fast)

Vercel is perfect for Next.js applications with unlimited free deployments.

#### Step 1: Prepare Frontend

Update `frontend/.env.production`:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

#### Step 2: Deploy

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd frontend

# Deploy
vercel

# Follow prompts:
# - Link to existing project? N
# - Project name? jobfinder-pro-frontend
# - Directory? ./
```

#### Alternative: Deploy via GitHub

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Import your repository
4. Configure:
   - Framework: Next.js
   - Root Directory: `frontend`
   - Environment Variables:
     - `NEXT_PUBLIC_API_URL`: Your backend URL

**Your frontend will be available at**: `https://jobfinder-pro.vercel.app`

---

### Netlify (Alternative)

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Navigate to frontend and build
cd frontend
npm run build

# Deploy
netlify deploy --prod

# Set environment variable in Netlify dashboard
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

---

## Database Options

### Option 1: Neon (Recommended)

**Free Tier**: 512MB storage, 3GB data transfer/month

#### Setup:

1. Visit [neon.tech](https://neon.tech)
2. Sign up with GitHub
3. Create new project:
   - Name: jobfinder-pro
   - Region: Choose closest to users
   - Postgres version: 16

4. Copy connection string:
```
postgres://user:password@ep-xxxxx.region.neon.tech/main?sslmode=require
```

5. Run migrations:
```bash
# Set DATABASE_URL locally
export DATABASE_URL=<your-neon-url>

# Run migrations
alembic upgrade head
```

---

### Option 2: Supabase

**Free Tier**: 500MB database, 50MB file storage, 2GB bandwidth

#### Setup:

1. Visit [supabase.com](https://supabase.com)
2. Create new project
3. Get connection string from Settings → Database
4. Use direct connection (not pooler) for migrations

```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
```

---

### Option 3: PlanetScale (MySQL)

**Note**: Requires schema changes since PlanetScale uses MySQL, not PostgreSQL.

**Free Tier**: 5GB storage, 1 billion row reads/month

---

### Option 4: ElephantSQL

**Free Tier**: 20MB storage (good for testing)

1. Visit [elephantsql.com](https://www.elephantsql.com/)
2. Create Tiny Turtle plan (free)
3. Copy URL and use in your app

---

## Redis/Cache Options

### Option 1: Upstash (Recommended)

**Free Tier**: 10K commands/day, 256MB storage

#### Setup:

1. Visit [upstash.com](https://upstash.com)
2. Create Redis database:
   - Name: jobfinder-redis
   - Type: Regional
   - Region: Choose closest to backend

3. Copy connection string:
```
redis://:password@region.upstash.io:PORT
```

4. Add to environment variables:
```env
REDIS_URL=<upstash-url>
CELERY_BROKER_URL=<upstash-url>
CELERY_RESULT_BACKEND=<upstash-url>
```

---

### Option 2: Redis Labs

**Free Tier**: 30MB storage

1. Visit [redis.com](https://redis.com)
2. Create free database
3. Use provided connection string

---

### Option 3: Render Redis

If using Render for backend, add Redis service (paid, but $1/month for 25MB).

---

## Complete Free Stack

### Architecture

```
[User Browser]
      ↓
[Vercel - Frontend] → [Render - Backend API]
                            ↓
                      [Neon - PostgreSQL]
                      [Upstash - Redis]
```

### Step-by-Step Setup

#### 1. Setup Database (Neon)

```bash
# Create account at neon.tech
# Create project: jobfinder-pro
# Copy DATABASE_URL
export DATABASE_URL="postgres://user:pass@ep-xxx.neon.tech/main"

# Run migrations locally
alembic upgrade head
```

#### 2. Setup Redis (Upstash)

```bash
# Create account at upstash.com
# Create Redis database
# Copy REDIS_URL
export REDIS_URL="redis://:pass@region.upstash.io:PORT"
```

#### 3. Deploy Backend (Render)

```bash
# Push code to GitHub
git add .
git commit -m "Ready for deployment"
git push

# Go to render.com
# Create Web Service from GitHub repo
# Add environment variables:
DATABASE_URL=<neon-url>
REDIS_URL=<upstash-url>
SECRET_KEY=<generate-new>
JWT_SECRET_KEY=<generate-new>
SESSION_SECRET=<generate-new>

# Wait for deployment
```

#### 4. Deploy Frontend (Vercel)

```bash
# Update frontend/.env.production
echo "NEXT_PUBLIC_API_URL=https://jobfinder-pro-api.onrender.com" > frontend/.env.production

# Deploy
cd frontend
vercel --prod

# Or connect GitHub repo via Vercel dashboard
```

#### 5. Test Your Deployment

```bash
# Test backend
curl https://jobfinder-pro-api.onrender.com/health

# Test frontend
# Visit: https://jobfinder-pro.vercel.app
```

---

## Environment Variables Checklist

### Backend Environment Variables

```env
# Database
DATABASE_URL=<neon-postgres-url>

# Redis
REDIS_URL=<upstash-redis-url>
CELERY_BROKER_URL=<upstash-redis-url>
CELERY_RESULT_BACKEND=<upstash-redis-url>

# Security (generate new for production!)
SECRET_KEY=<python-secrets-token>
JWT_SECRET_KEY=<python-secrets-token>
SESSION_SECRET=<python-secrets-token>

# API Keys (optional)
ADZUNA_APP_ID=<your-adzuna-app-id>
ADZUNA_API_KEY=<your-adzuna-api-key>

# Application
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Frontend Environment Variables

```env
NEXT_PUBLIC_API_URL=<your-backend-url>
```

---

## Cost Breakdown

| Service | Free Tier | Limits | Cost After |
|---------|-----------|--------|------------|
| **Render** (Backend) | 750 hrs/month | Auto-sleeps after 15min inactivity | $7/month for always-on |
| **Vercel** (Frontend) | Unlimited | 100GB bandwidth/month | $20/month for Pro |
| **Neon** (Database) | 512MB | 3GB transfer/month | $19/month for 10GB |
| **Upstash** (Redis) | 10K commands/day | 256MB storage | $0.20/100K commands |

**Total Free Tier**: Perfect for development, testing, and small projects (up to ~1000 users/month)

---

## Monitoring & Maintenance

### Free Monitoring Tools

1. **Sentry** (Error Tracking)
   - Free tier: 5K errors/month
   - Setup: [docs.sentry.io](https://docs.sentry.io)

2. **LogTail** (Log Management)
   - Free tier: 1GB/month
   - Setup: [logtail.com](https://logtail.com)

3. **UptimeRobot** (Uptime Monitoring)
   - Free tier: 50 monitors
   - Setup: [uptimerobot.com](https://uptimerobot.com)

### Health Checks

Add this to your backend (already included):

```python
# api/main.py
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

Configure UptimeRobot to ping `https://your-backend.onrender.com/health` every 5 minutes to prevent Render from sleeping.

---

## Scaling Up

When you outgrow free tiers:

### Backend
- **Render**: Upgrade to $7/month starter plan (always-on)
- **Railway**: Add credits ($5/month minimum)
- **Fly.io**: Deploy with persistent disk ($1.94/month for 1GB)

### Database
- **Neon**: Scale plan ($19/month for 10GB)
- **Supabase**: Pro plan ($25/month)
- **AWS RDS**: Free tier for 12 months, then $15-30/month

### Redis
- **Upstash**: Pay-as-you-go ($0.20/100K commands)
- **Render Redis**: $1/month for 25MB

---

## Troubleshooting

### Backend Won't Start on Render

**Issue**: Build succeeds but service doesn't start

**Solution**:
```bash
# Ensure requirements.txt includes all dependencies
pip freeze > requirements.txt

# Check Start Command uses $PORT
uvicorn api.main:app --host 0.0.0.0 --port $PORT

# Check logs in Render dashboard
```

### Database Connection Fails

**Issue**: `could not connect to server`

**Solution**:
```env
# Ensure connection string includes sslmode
DATABASE_URL=postgres://user:pass@host/db?sslmode=require

# For Neon, always use sslmode=require
# For Supabase, use connection pooler for production
```

### Frontend Can't Reach Backend

**Issue**: CORS errors or network failures

**Solution**:
```python
# In api/main.py, ensure CORS allows your frontend
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jobfinder-pro.vercel.app",
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Celery Tasks Not Processing

**Issue**: Background tasks stuck in queue

**Solution**:

For free tiers without background workers, consider:

1. **Disable Celery** and process tasks synchronously:
```python
# In api/app/routes/resume.py
# Instead of: task = process_resume.delay(resume_id)
# Use: process_resume_sync(resume_id)
```

2. **Use Render Background Workers** ($7/month):
   - Add new service: Background Worker
   - Start Command: `celery -A api.app.celery_app worker --loglevel=info`

---

## Next Steps

1. **Setup Custom Domain** (optional):
   - Vercel: Add custom domain (free with your domain)
   - Render: Add custom domain (free)

2. **Enable HTTPS** (automatic on all platforms)

3. **Setup CI/CD**:
   - All platforms auto-deploy on git push
   - Configure branch previews in Vercel

4. **Add Monitoring**:
   - Setup Sentry for error tracking
   - Configure UptimeRobot for uptime monitoring

5. **Backup Database**:
   - Neon: Automatic daily backups
   - Setup manual backup script for critical data

---

**Need Help?** 
- Check platform-specific documentation
- Join communities: Render Discord, Vercel Discord
- Review logs in respective dashboards

**Last Updated**: October 27, 2025
