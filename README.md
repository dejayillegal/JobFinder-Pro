# JobFinder Pro 🎯

**Production-grade SaaS platform for resume-driven job matching powered by AI**

JobFinder Pro is a complete job matching platform that uses machine learning to match resumes with relevant job postings from multiple sources (Adzuna, Indeed, Jooble, LinkedIn, Naukri). Upload your resume, and the system will find the best jobs for you with explainable AI scoring.

## 🌟 Key Features

### Core Functionality
- **Resume Parsing**: Supports PDF, DOCX, and TXT formats with advanced NLP extraction (spaCy)
- **Multi-Source Job Aggregation**: Fetches jobs from Adzuna API with mock connectors for Indeed, Jooble, LinkedIn, and Naukri
- **AI-Powered Matching**: Explainable scoring algorithm (Skills 60%, Seniority 25%, Location 15%)
- **India-Focus**: Optimized for India-wide jobs with priority for Bangalore and Remote positions
- **Background Processing**: Celery + Redis for async job processing
- **JWT Authentication**: Secure user authentication with access and refresh tokens

### Technical Stack
- **Backend**: FastAPI + SQLAlchemy + Alembic + PostgreSQL
- **Frontend**: Next.js + TypeScript + Tailwind CSS
- **ML/NLP**: spaCy for entity extraction and skills matching
- **Task Queue**: Celery + Redis for background processing
- **Observability**: Prometheus metrics, structured logging (JSON)
- **Database**: PostgreSQL with Alembic migrations

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL database
- Redis server (for Celery)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd jobfinder-pro
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your credentials
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

4. **Run database migrations**
```bash
alembic upgrade head
```

5. **Install frontend dependencies**
```bash
cd frontend
npm install
cd ..
```

6. **Start the services**
```bash
# Terminal 1: Start API server
uvicorn api.main:app --host 0.0.0.0 --port 5000 --reload

# Terminal 2: Start Celery worker
celery -A api.app.celery_app worker --loglevel=info

# Terminal 3: Start frontend (development)
cd frontend && npm run dev
```

7. **Access the application**
- Frontend: http://localhost:3000
- API Docs: http://localhost:5000/docs
- Metrics: http://localhost:5000/metrics

## 📁 Project Structure

```
jobfinder-pro/
├── api/                          # Backend FastAPI application
│   ├── main.py                   # Main FastAPI app entry point
│   └── app/
│       ├── core/                 # Core configuration and utilities
│       │   ├── config.py         # Environment settings
│       │   ├── database.py       # Database connection
│       │   ├── security.py       # JWT and password hashing
│       │   └── logging.py        # Structured logging
│       ├── models/               # SQLAlchemy database models
│       │   ├── user.py           # User model
│       │   ├── resume.py         # Resume model
│       │   └── job.py            # Job, JobMatch, ProcessingJob models
│       ├── services/             # Business logic services
│       │   ├── resume_parser.py  # Resume parsing (PDF/DOCX/TXT)
│       │   └── matcher.py        # AI matching algorithm
│       ├── connectors/           # Job source connectors
│       │   ├── adzuna.py         # Adzuna API connector
│       │   ├── indeed.py         # Indeed mock connector
│       │   ├── jooble.py         # Jooble mock connector
│       │   ├── linkedin.py       # LinkedIn mock connector
│       │   └── naukri.py         # Naukri mock connector
│       ├── routes/               # API endpoints
│       │   ├── auth.py           # Authentication endpoints
│       │   ├── resume.py         # Resume upload endpoints
│       │   ├── matches.py        # Job matches endpoints
│       │   ├── admin.py          # Admin endpoints
│       │   └── metrics.py        # Prometheus metrics
│       ├── celery_app.py         # Celery configuration
│       └── tasks.py              # Background tasks
├── frontend/                     # Next.js frontend
│   ├── pages/                    # Next.js pages
│   │   ├── index.tsx             # Landing page
│   │   ├── login.tsx             # Login page
│   │   ├── register.tsx          # Registration page
│   │   ├── upload.tsx            # Resume upload page
│   │   └── matches.tsx           # Job matches dashboard
│   └── lib/
│       └── api.ts                # API client
├── alembic/                      # Database migrations
│   └── versions/
│       └── 001_initial_schema.py # Initial schema
├── tests/                        # Test suite
│   ├── test_parser.py            # Resume parser tests
│   ├── test_matcher.py           # Matching algorithm tests
│   └── test_connectors.py        # Connector tests
├── docker/                       # Docker configurations
│   ├── Dockerfile.api            # API Dockerfile
│   ├── Dockerfile.frontend       # Frontend Dockerfile
│   └── docker-compose.yml        # Local development setup
├── k8s/                          # Kubernetes manifests
│   └── helm/                     # Helm chart
├── .github/
│   └── workflows/
│       └── ci.yml                # CI/CD pipeline
├── scripts/                      # Utility scripts
│   ├── dev_start.sh              # Development startup script
│   ├── export_zip.py             # Export project as ZIP
│   └── cli.py                    # CLI utilities
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
└── README.md                     # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/jobfinder

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
SESSION_SECRET=your-session-secret-here

# API Keys (optional - defaults to mock data)
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_API_KEY=your-adzuna-api-key

# Application
DEBUG=true
LOG_LEVEL=INFO
```

### API Keys

- **Adzuna**: Sign up at https://developer.adzuna.com/ to get API credentials
- Other connectors (Indeed, Jooble, LinkedIn, Naukri) use mock data by default

## 📊 Matching Algorithm

The explainable AI matching algorithm uses weighted scoring:

```
Total Score = (Skills Match × 0.6) + (Seniority Match × 0.25) + (Location Match × 0.15)
```

### Skills Match (60%)
- Exact skill matching with case-insensitive comparison
- Weighted by importance (Python, Java, AWS, etc. have higher weights)
- Normalized to 0-100 scale

### Seniority Match (25%)
- Matches candidate experience level with job requirements
- Entry → Junior → Mid → Senior → Lead → Director
- Partial credit for adjacent levels

### Location Match (15%)
- Prioritizes Bangalore and Remote positions for India-focused search
- Supports exact location matching
- Handles remote work preferences

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov-report=html

# Run specific test file
pytest tests/test_matcher.py -v
```

## 📈 Monitoring

### Prometheus Metrics

Available at `/metrics` endpoint:

- `http_requests_total`: Total HTTP requests
- `http_request_duration_seconds`: Request latency
- `resume_parsing_duration_seconds`: Resume parsing time
- `job_matching_duration_seconds`: Matching computation time

### Structured Logging

All logs are in JSON format for easy parsing:

```json
{
  "timestamp": "2025-10-27T12:00:00+00:00",
  "level": "INFO",
  "message": "Resume parsed successfully",
  "user_id": 123,
  "resume_id": 456
}
```

## 🔐 Security Features

- **JWT Authentication**: Access and refresh tokens
- **Password Hashing**: bcrypt with salt
- **Rate Limiting**: Prevents abuse
- **Input Validation**: Pydantic models
- **SQL Injection Prevention**: SQLAlchemy ORM
- **CORS Protection**: Configurable origins

## 🚢 Deployment

### Docker Compose (Local)

```bash
docker-compose up -d
```

### Kubernetes (Production)

```bash
# Using Helm
helm install jobfinder ./k8s/helm -f values.yaml

# Using kubectl
kubectl apply -f k8s/
```

### Environment-Specific Configuration

- **Development**: Hot reload, debug logging, mock APIs
- **Production**: Optimized builds, error reporting, real APIs

## 🛠 Development Scripts

### Start Development Environment
```bash
./scripts/dev_start.sh
```

### Export Project as ZIP
```bash
python scripts/export_zip.py
```

### CLI Utilities
```bash
# Create admin user
python scripts/cli.py create-admin --email admin@example.com

# Reindex all jobs
python scripts/cli.py reindex-jobs

# Database cleanup
python scripts/cli.py cleanup-old-jobs --days 30
```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📜 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [Adzuna API](https://developer.adzuna.com/) for job data
- [spaCy](https://spacy.io/) for NLP capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent framework

## 📞 Support

For issues and feature requests, please use the GitHub issue tracker.

---

Built with ❤️ for job seekers in India
