# GitHub Actions Setup Guide

This guide explains how to configure GitHub Actions for automated CI/CD deployment to multiple platforms.

## Table of Contents
- [Overview](#overview)
- [Available Workflows](#available-workflows)
- [Required Secrets](#required-secrets)
- [Platform Setup](#platform-setup)
- [Workflow Configuration](#workflow-configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project includes comprehensive GitHub Actions workflows for:
- ✅ **Automated Testing**: Run tests on every PR and push
- ✅ **Code Quality**: Linting, formatting, type checking
- ✅ **Security Scanning**: Dependency and vulnerability checks
- ✅ **Multi-Platform Deployment**: Deploy to Vercel, Render, Railway, Fly.io, Netlify
- ✅ **Docker Images**: Build and push to GitHub Container Registry
- ✅ **Environment Management**: Separate staging and production deployments

---

## Available Workflows

### 1. CI/CD Workflows

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| **CI Tests** | `ci-tests.yml` | Push, PR | Run all tests, linting, security checks |
| **Docker Build** | `docker-build.yml` | Push to main | Build and push Docker images |
| **Deploy All** | `deploy-all-platforms.yml` | Manual | Deploy to all platforms at once |

### 2. Frontend Deployment

| Workflow | File | Platform | Free Tier |
|----------|------|----------|-----------|
| **Vercel** | `frontend-vercel.yml` | Vercel | ✅ Unlimited |
| **Netlify** | `frontend-netlify.yml` | Netlify | ✅ 100GB/month |

### 3. Backend Deployment

| Workflow | File | Platform | Free Tier |
|----------|------|----------|-----------|
| **Render** | `backend-render.yml` | Render | ✅ 750 hrs/month |
| **Railway** | `railway-deploy.yml` | Railway | ✅ $5 credit/month |
| **Fly.io** | `fly-io-deploy.yml` | Fly.io | ✅ 3GB RAM free |

---

## Required Secrets

### GitHub Repository Secrets

Add these secrets in: **Settings → Secrets and variables → Actions → New repository secret**

#### For All Workflows

```
# GitHub Container Registry (automatic)
GITHUB_TOKEN (automatically provided by GitHub)
```

#### For Vercel Deployment

```bash
# Get these from vercel.com dashboard
VERCEL_TOKEN=<your-vercel-token>
VERCEL_ORG_ID=<your-org-id>
VERCEL_PROJECT_ID=<your-project-id>

# API URL for production
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com

# API URL for staging (optional)
NEXT_PUBLIC_API_URL_STAGING=https://your-backend-staging.onrender.com
```

**How to get Vercel secrets:**
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Link project
cd frontend
vercel link

# Get project info
vercel project ls

# Get token from: https://vercel.com/account/tokens
```

#### For Render Deployment

```bash
# Get from render.com dashboard
RENDER_API_KEY=<your-render-api-key>
RENDER_SERVICE_ID=<your-production-service-id>
RENDER_SERVICE_ID_STAGING=<your-staging-service-id>
```

**How to get Render secrets:**
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Account Settings → API Keys → Create API Key
3. Copy your service ID from service URL: `https://dashboard.render.com/web/srv-XXXXX`

#### For Railway Deployment

```bash
RAILWAY_TOKEN=<your-railway-token>
```

**How to get Railway token:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Get token from: https://railway.app/account/tokens
```

#### For Fly.io Deployment

```bash
FLY_API_TOKEN=<your-fly-api-token>
```

**How to get Fly.io token:**
```bash
# Install Flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Get token
flyctl auth token
```

#### For Netlify Deployment

```bash
NETLIFY_AUTH_TOKEN=<your-netlify-token>
NETLIFY_SITE_ID=<your-site-id>
```

**How to get Netlify secrets:**
1. Go to [app.netlify.com](https://app.netlify.com)
2. User Settings → Applications → Personal Access Tokens
3. Site ID from: Site Settings → General → Site details

#### For Code Quality (Optional)

```bash
# For SonarCloud
SONAR_TOKEN=<your-sonar-token>

# For Codecov
CODECOV_TOKEN=<your-codecov-token>

# For Snyk
SNYK_TOKEN=<your-snyk-token>
```

---

## Platform Setup

### 1. Vercel Setup

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy frontend for the first time
cd frontend
vercel

# Link to project
vercel link

# Set environment variables in Vercel dashboard:
# - NEXT_PUBLIC_API_URL
```

### 2. Render Setup

1. **Create Web Service**:
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - New → Web Service
   - Connect GitHub repository
   - Configure:
     ```
     Name: jobfinder-pro-api
     Environment: Python 3
     Build Command: pip install -r requirements.txt && python -m spacy download en_core_web_sm
     Start Command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
     ```

2. **Add Environment Variables** in Render dashboard:
   ```
   DATABASE_URL=<neon-postgres-url>
   REDIS_URL=<upstash-redis-url>
   SECRET_KEY=<generate-random>
   JWT_SECRET_KEY=<generate-random>
   SESSION_SECRET=<generate-random>
   ```

3. **Enable Auto-Deploy**:
   - Settings → Auto-Deploy → Yes

### 3. Railway Setup

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add PostgreSQL
railway add postgresql

# Add Redis
railway add redis

# Deploy
railway up
```

### 4. Fly.io Setup

```bash
# Install Flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app (follow prompts)
flyctl launch

# Deploy
flyctl deploy
```

---

## Workflow Configuration

### Automatic Deployments

**On Push to `main` branch:**
- ✅ Runs all tests
- ✅ Builds Docker images
- ✅ Deploys to production (Vercel + Render)
- ✅ Runs post-deployment smoke tests

**On Push to `staging` branch:**
- ✅ Runs all tests
- ✅ Deploys to staging environment

**On Pull Request:**
- ✅ Runs all tests
- ✅ Creates preview deployment on Vercel
- ✅ Comments deployment URL on PR

### Manual Deployments

Trigger manual deployment from GitHub:
1. Go to **Actions** tab
2. Select **Deploy to All Platforms**
3. Click **Run workflow**
4. Choose environment (staging/production)
5. Click **Run workflow**

---

## Usage

### Example 1: Deploy Everything to Production

```bash
# 1. Make your changes
git checkout -b feature/new-feature

# 2. Commit and push
git add .
git commit -m "Add new feature"
git push origin feature/new-feature

# 3. Create PR on GitHub
# → Automatic tests run
# → Preview deployment created

# 4. Merge PR to main
# → Automatic deployment to production
```

### Example 2: Deploy Only Frontend

```bash
# Make changes to frontend only
cd frontend
# ... make changes ...

git add frontend/
git commit -m "Update frontend"
git push

# GitHub Actions automatically:
# 1. Detects changes in frontend/
# 2. Runs frontend tests
# 3. Deploys to Vercel
```

### Example 3: Manual Deploy to Staging

1. Go to GitHub repo → **Actions**
2. Select **Deploy to All Platforms**
3. Click **Run workflow**
4. Select `staging` environment
5. Click **Run workflow**

---

## Branch Strategy

Recommended Git workflow:

```
main (production)
  ↑
staging (testing)
  ↑
develop (development)
  ↑
feature/* (features)
```

**Deployment Flow:**
1. **Feature branches** → Create PR → Auto-test + preview
2. **Develop branch** → Continuous integration testing
3. **Staging branch** → Auto-deploy to staging environment
4. **Main branch** → Auto-deploy to production

---

## Environment Variables by Workflow

### Frontend Workflows Need:

```bash
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
NEXT_PUBLIC_API_URL
NEXT_PUBLIC_API_URL_STAGING (optional)

# Or for Netlify
NETLIFY_AUTH_TOKEN
NETLIFY_SITE_ID
```

### Backend Workflows Need:

```bash
RENDER_API_KEY
RENDER_SERVICE_ID
RENDER_SERVICE_ID_STAGING (optional)

# Or for Railway
RAILWAY_TOKEN

# Or for Fly.io
FLY_API_TOKEN
```

### CI/Test Workflows Need:

```bash
# Optional, for enhanced features
CODECOV_TOKEN
SONAR_TOKEN
SNYK_TOKEN
```

---

## Troubleshooting

### Issue: Workflow fails with "Resource not accessible"

**Solution:**
```yaml
# In workflow file, add permissions:
permissions:
  contents: read
  packages: write
  pull-requests: write
```

### Issue: Vercel deployment fails

**Solution:**
1. Check `VERCEL_TOKEN` is valid
2. Verify `VERCEL_PROJECT_ID` and `VERCEL_ORG_ID`
3. Ensure `vercel` CLI is latest version in workflow

```bash
# Update Vercel CLI in workflow
- name: Install Vercel CLI
  run: npm install --global vercel@latest
```

### Issue: Database migrations fail

**Solution:**
1. Migrations should run in platform dashboard, not GitHub Actions
2. Or use SSH/remote command execution:

```yaml
- name: Run migrations
  run: |
    railway run alembic upgrade head
  env:
    RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### Issue: Docker build fails with space issues

**Solution:**
```yaml
# Add cache cleanup
- name: Clean up Docker
  run: docker system prune -af
```

### Issue: Secrets not found

**Solution:**
1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Verify secret names match exactly (case-sensitive)
3. Re-add secrets if needed

### Issue: Tests fail in CI but pass locally

**Solution:**
```yaml
# Ensure services are healthy before running tests
services:
  postgres:
    # ... config ...
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

---

## Advanced Configuration

### Custom Deployment Conditions

Deploy only when specific files change:

```yaml
on:
  push:
    paths:
      - 'api/**'
      - 'requirements.txt'
    branches:
      - main
```

### Deploy Specific Services

```yaml
# Deploy only if API changed
jobs:
  deploy:
    if: contains(github.event.head_commit.modified, 'api/')
```

### Matrix Testing

Test against multiple versions:

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
    node-version: ['18', '20']
```

### Slack Notifications

Add notification step:

```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Deployment to production completed!"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## Monitoring Deployments

### View Deployment Status

1. **GitHub Actions Tab**:
   - See all workflow runs
   - View logs for each step
   - Re-run failed workflows

2. **Platform Dashboards**:
   - Vercel: [vercel.com/dashboard](https://vercel.com/dashboard)
   - Render: [dashboard.render.com](https://dashboard.render.com)
   - Railway: [railway.app](https://railway.app)

3. **Commit Status Checks**:
   - Green checkmark = successful deployment
   - Red X = failed deployment
   - Yellow dot = in progress

---

## Cost Optimization

### Free Tier Limits

| Platform | Free Tier | After Limit |
|----------|-----------|-------------|
| Vercel | Unlimited | $20/month Pro |
| Netlify | 100GB bandwidth | $19/month Pro |
| Render | 750 hours/month | $7/month always-on |
| Railway | $5 credit/month | Pay-as-you-go |
| Fly.io | 3GB RAM | $1.94/GB/month |

### Tips to Stay Free

1. **Render**: Use only when needed (auto-sleep after 15min)
2. **Railway**: Monitor credit usage dashboard
3. **Vercel**: Unlimited for personal projects
4. **Docker**: Use GitHub Container Registry (free with GitHub)

---

## Security Best Practices

1. **Never commit secrets** to repository
2. **Use environment-specific secrets** (staging vs production)
3. **Enable branch protection** on main branch
4. **Require PR reviews** before merging
5. **Enable security scanning** (Dependabot, CodeQL)
6. **Rotate secrets** regularly
7. **Use least-privilege tokens** (read-only when possible)

---

## Next Steps

1. ✅ Add all required secrets to GitHub
2. ✅ Test workflows with a feature branch
3. ✅ Set up branch protection rules
4. ✅ Configure platform webhooks
5. ✅ Add status badges to README
6. ✅ Set up monitoring and alerts

---

## Status Badges

Add these to your README.md:

```markdown
![CI Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/CI%20-%20Tests%20and%20Quality%20Checks/badge.svg)
![Deploy Frontend](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Deploy%20Frontend%20to%20Vercel/badge.svg)
![Deploy Backend](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Deploy%20Backend%20to%20Render/badge.svg)
```

---

**Last Updated**: October 27, 2025
**Version**: 1.0.0
