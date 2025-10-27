# JobFinder Pro 🎯

**Production-grade SaaS platform for resume-driven job matching powered by AI**

JobFinder Pro is a complete job matching platform that uses machine learning to match resumes with relevant job postings from multiple sources (Adzuna, Indeed RSS, Jooble, LinkedIn, Naukri). Upload your resume, and the system will find the best jobs for you with explainable AI scoring.

## 🌟 Key Features

### Core Functionality
- **Resume Parsing**: Supports PDF, DOCX, and TXT formats with advanced NLP extraction (spaCy)
- **Multi-Source Job Aggregation**: 
  - Adzuna API (real jobs with free tier)
  - RSS feed aggregation for Indeed and other sources
  - Mock connectors for testing and development
- **AI-Powered Matching**: Explainable TF-IDF scoring algorithm with skills, experience, and location matching
- **India-Focus**: Optimized for India-wide jobs with priority for Bangalore and Remote positions
- **Background Processing**: Celery + Redis for async job processing
- **JWT Authentication**: Secure user authentication with access and refresh tokens
- **Privacy-First**: GDPR-compliant with configurable data retention

### Technical Stack
- **Backend**: FastAPI + SQLAlchemy + Alembic + PostgreSQL
- **Frontend**: Next.js + TypeScript + Tailwind CSS
- **ML/NLP**: spaCy for entity extraction and TF-IDF for matching
- **Task Queue**: Celery + Redis for background processing
- **Observability**: Prometheus metrics, structured logging (JSON)
- **Database**: PostgreSQL with Alembic migrations

## 🚀 Quick Start

### Option 1: Replit Deployment (Recommended)

This project is already configured for Replit:

1. **Environment Setup**: All secrets are configured in Replit Secrets
2. **Start Services**:
   - Click the **Run** button to start the Frontend
   - Use workflow dropdown to start "Backend API"
   - Use workflow dropdown to start "Celery Worker" (optional, for background jobs)
3. **Access**:
   - Frontend: Your Repl's webview URL
   - API Docs: `https://your-repl-url.repl.co:8000/docs`

### Option 2: Local Development

**Prerequisites:**
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

**Automated Setup:**

```bash
# Clone repository
git clone <repository-url>
cd jobfinder-pro

# Run automated setup
chmod +x scripts/local_setup.sh
./scripts/local_setup.sh
```

**Manual Setup:**

```bash
# 1. Environment setup
cp .env.example .env
# Edit .env with your credentials

# 2. Install Python dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Setup database
createdb jobfinder
alembic upgrade head

# 4. Install frontend dependencies
cd frontend && npm install && cd ..

# 5. Start services (3 separate terminals)

# Terminal 1 - Backend API
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Celery Worker
celery -A api.app.celery_app worker --loglevel=info

# Terminal 3 - Frontend
cd frontend && npm run dev
```

**Access the Application:**
- Frontend: http://localhost:5000
- API Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

## 📁 Project Structure

```
jobfinder-pro/
├── api/                          # Backend FastAPI application
│   ├── app/
│   │   ├── core/                 # Config, database, security
│   │   ├── models/               # SQLAlchemy models
│   │   ├── services/             # Business logic (parser, matcher)
│   │   ├── connectors/           # Job source integrations
│   │   ├── scrapers/             # RSS and web scrapers
│   │   ├── routes/               # API endpoints
│   │   └── utils/                # Utilities (privacy, rate limiting)
│   └── main.py                   # FastAPI entry point
├── frontend/                     # Next.js frontend
│   ├── pages/                    # React pages
│   └── lib/                      # API client
├── alembic/                      # Database migrations
├── tests/                        # Test suite
├── scripts/                      # Setup and utility scripts
├── docker/                       # Docker configurations
└── .github/workflows/            # CI/CD pipelines
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

```bash
# Database
DATABASE_URL=postgresql://localhost:5432/jobfinder

# Redis
REDIS_URL=redis://localhost:6379/0

# Security (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# API Keys (optional - uses RSS/mock if not provided)
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_API_KEY=your-adzuna-api-key

# Privacy
STORE_RESUME_RAW=false           # Don't store raw resume text (GDPR)
ANONYMIZE_JOBS=true              # Anonymize job data

# Matching
EMBEDDING_BACKEND=tfidf          # Use TF-IDF for matching
```

### Getting API Keys

**Adzuna (FREE - Recommended):**
1. Visit https://developer.adzuna.com/
2. Sign up and create an application
3. Copy your App ID and API Key
4. Free tier: 1000 API calls/month

**Other sources use RSS feeds** (no API keys needed)

## 📊 Matching Algorithm

The AI matching uses TF-IDF (Term Frequency-Inverse Document Frequency):

```python
# Skills matching with TF-IDF vectors
skills_similarity = cosine_similarity(resume_vector, job_vector)

# Combined with location and experience matching
total_score = (skills * 0.6) + (experience * 0.25) + (location * 0.15)
```

**Features:**
- Weighted skill matching (60%)
- Experience level matching (25%)
- Location preference (15%)
- Explainable results with detailed breakdowns

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=api --cov-report=html

# Run specific tests
pytest tests/test_matcher.py -v

# Validate setup
python tests/validate_setup.py
```

## 📈 Monitoring

### Prometheus Metrics

Available at `/metrics`:
- `http_requests_total`: Total HTTP requests
- `http_request_duration_seconds`: Request latency
- `resume_parsing_duration_seconds`: Resume parsing time
- `job_matching_duration_seconds`: Matching computation time

### Structured Logging

All logs are in JSON format:

```json
{
  "timestamp": "2025-01-27T12:00:00+00:00",
  "level": "INFO",
  "message": "Resume parsed successfully",
  "user_id": 123,
  "resume_id": 456
}
```

## 🔐 Security & Privacy

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt with salt
- **GDPR Compliance**: Configurable data retention
- **Privacy-First**: Raw resume text not stored by default
- **Rate Limiting**: Prevents abuse
- **Input Validation**: Pydantic models

See [PRIVACY_AND_GDPR.md](PRIVACY_AND_GDPR.md) for details.

## 🚢 Deployment

### Replit Deployment

1. Click the **Deploy** button in Replit
2. Select **Autoscale** deployment type
3. Configure:
   - Build Command: `cd frontend && npm run build`
   - Run Command: `cd frontend && npm run start`
4. Deploy and access at your Repl URL

### Local Production Mode

```bash
# Using PM2 (recommended)
npm install -g pm2
pm2 start ecosystem.config.js
pm2 save

# Or using production script
chmod +x scripts/production_start.sh
./scripts/production_start.sh
```

See [SETUP.md](SETUP.md) for detailed deployment instructions.

## 🛠 Development Scripts

```bash
# Setup
make install              # Install all dependencies
make dev                  # Start development environment

# Testing
make test                 # Run all tests
make test-coverage        # Run with coverage
make test-validate        # Validate setup

# Utilities
make lint                 # Run linters
make format               # Auto-format code
make clean                # Remove build artifacts

# Database
make migrate              # Run migrations
make migrate-create       # Create new migration
```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📚 Documentation

- [Quick Start Guide](QUICK_START.md) - 5-minute setup
- [Local Setup Guide](SETUP_LOCAL.md) - Detailed local development
- [Deployment Guide](SETUP.md) - Production deployment
- [GitHub Actions Setup](GITHUB_ACTIONS_SETUP.md) - CI/CD configuration
- [Privacy & GDPR](PRIVACY_AND_GDPR.md) - Privacy features

## 📞 Support

- GitHub Issues: Report bugs or request features
- Documentation: Check the docs above
- Tests: Run `python tests/validate_setup.py` for diagnostics

## 📜 License

MIT License - see LICENSE file for details

---

Built with ❤️ for job seekers worldwide | Optimized for India 🇮🇳