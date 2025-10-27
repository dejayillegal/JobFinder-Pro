# JobFinder Pro - Replit Project Documentation

## Project Overview

**JobFinder Pro** is a production-grade SaaS platform for AI-powered resume-driven job matching. The system allows users to upload their resumes (PDF/DOCX/TXT), which are then intelligently matched against jobs from multiple sources (Adzuna API + mock connectors for Indeed, Jooble, LinkedIn, Naukri) using an explainable AI scoring algorithm.

### Key Features
- Resume parsing with spaCy NER (PDF/DOCX/TXT support)
- Multi-source job aggregation (Adzuna real API + mock connectors)
- Explainable AI matching (Skills 60%, Seniority 25%, Location 15%)
- India-focused with Bangalore and Remote prioritization
- JWT authentication
- Celery + Redis background processing
- Prometheus metrics and structured logging
- Full CRUD APIs with FastAPI
- Next.js frontend with TypeScript

## Recent Changes

### 2025-10-27: Bug Fixes and Initial Setup
- Fixed SQLAlchemy reserved name conflict: renamed `metadata` column to `job_metadata`
- Removed `EmailStr` type to avoid pydantic[email] dependency issues
- Successfully configured and started API Server workflow
- Database tables created and verified
- All routes operational (auth, resume, matches, admin, metrics)

## Project Architecture

### Backend (FastAPI + SQLAlchemy + PostgreSQL)
```
api/
├── main.py                   # FastAPI application entry point
└── app/
    ├── core/                 # Core configuration and utilities
    │   ├── config.py         # Environment settings (SECRET_KEY, DATABASE_URL, etc.)
    │   ├── database.py       # SQLAlchemy database connection
    │   ├── security.py       # JWT token generation, password hashing
    │   └── logging.py        # Structured JSON logging
    ├── models/               # SQLAlchemy ORM models
    │   ├── user.py           # User authentication model
    │   ├── resume.py         # Resume storage and parsed data
    │   └── job.py            # Job, JobMatch, ProcessingJob models
    ├── services/             # Business logic services
    │   ├── resume_parser.py  # PDF/DOCX/TXT parsing with spaCy
    │   └── matcher.py        # AI matching algorithm with scoring
    ├── connectors/           # Job source integrations
    │   ├── adzuna.py         # Adzuna API (real) with mock fallback
    │   ├── indeed.py         # Indeed mock connector
    │   ├── jooble.py         # Jooble mock connector
    │   ├── linkedin.py       # LinkedIn mock connector
    │   └── naukri.py         # Naukri mock connector
    ├── routes/               # API endpoints
    │   ├── auth.py           # POST /auth/register, /auth/login, /auth/refresh
    │   ├── resume.py         # POST /resume/upload, GET /resume/status
    │   ├── matches.py        # GET /matches/
    │   ├── admin.py          # POST /admin/reindex
    │   └── metrics.py        # GET /metrics (Prometheus)
    ├── celery_app.py         # Celery configuration with Redis
    └── tasks.py              # Background tasks (resume processing, job fetching)
```

### Frontend (Next.js + TypeScript + Tailwind)
```
frontend/
├── pages/
│   ├── index.tsx             # Landing page
│   ├── login.tsx             # User login
│   ├── register.tsx          # User registration
│   ├── upload.tsx            # Resume upload interface
│   └── matches.tsx           # Job matches dashboard
└── lib/
    └── api.ts                # API client utilities
```

### Database Schema
- **users**: User accounts (email, hashed_password, is_admin)
- **resumes**: Uploaded resumes with parsed data
- **jobs**: Job listings from external sources
- **job_matches**: Match results with scores and explanations
- **processing_jobs**: Background job tracking

## Development Workflow

### Starting the Application

**Replit Environment (Current):**
The API Server workflow is already configured and running on port 5000.

**Local Development:**
```bash
# Start all services
./scripts/dev_start.sh

# Or manually:
# Terminal 1: API
uvicorn api.main:app --host 0.0.0.0 --port 5000 --reload

# Terminal 2: Celery
celery -A api.app.celery_app worker --loglevel=info

# Terminal 3: Frontend
cd frontend && npm run dev
```

### Database Migrations

```bash
# Apply migrations
alembic upgrade head

# Create new migration
alembic revision -m "description"

# Rollback one migration
alembic downgrade -1
```

### Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=api --cov-report=html

# Specific test file
pytest tests/test_matcher.py -v
```

## Configuration

### Environment Variables

**Required:**
- `DATABASE_URL`: PostgreSQL connection string (auto-configured in Replit)
- `REDIS_URL`: Redis connection for Celery (default: redis://localhost:6379/0)
- `SECRET_KEY`: JWT signing key (auto-generated in Replit)
- `SESSION_SECRET`: Session encryption key (auto-configured)

**Optional:**
- `ADZUNA_APP_ID`: Adzuna API application ID (uses mock if not set)
- `ADZUNA_API_KEY`: Adzuna API key (uses mock if not set)
- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)

## Matching Algorithm

The AI matching algorithm uses weighted scoring:

```python
score = (skills_match * 0.6) + (seniority_match * 0.25) + (location_match * 0.15)
```

### Skills Match (60%)
- Exact skill matching (case-insensitive)
- Higher weight for critical skills (Python, Java, AWS, etc.)
- Normalized to 0-100 scale

### Seniority Match (25%)
- Entry → Junior → Mid → Senior → Lead → Director
- Exact match: 100%
- Adjacent levels: 50%
- Two levels apart: 25%

### Location Match (15%)
- Bangalore: 100% (priority)
- Remote: 100% (priority)
- Other India locations: 50%
- International: 25%

## API Endpoints

### Authentication
- `POST /auth/register` - Create new user account
- `POST /auth/login` - Login and get JWT token
- `POST /auth/refresh` - Refresh access token

### Resume Management
- `POST /resume/upload` - Upload resume (PDF/DOCX/TXT)
- `GET /resume/status/{job_id}` - Check processing status

### Job Matching
- `GET /matches/` - Get job matches for authenticated user
- `GET /matches/{match_id}` - Get specific match details

### Admin
- `POST /admin/reindex` - Trigger job reindexing (admin only)

### Monitoring
- `GET /metrics` - Prometheus metrics endpoint
- `GET /health` - Health check endpoint

## User Preferences

### Code Style
- **Python**: PEP 8, type hints, docstrings
- **TypeScript**: Functional components, named exports
- **Imports**: Organized (stdlib, third-party, local)
- **Comments**: Clear, concise, for complex logic only

### Database Operations
- Use Alembic for migrations (never manual SQL)
- Use SQLAlchemy ORM (no raw SQL except for debugging)
- Reserved column names: Avoid `metadata`, `type`, `id` conflicts

### Error Handling
- Structured logging with JSON format
- Proper HTTP status codes
- Detailed error messages in development
- Generic messages in production

## Known Issues and Notes

### Fixed Issues
- ✅ SQLAlchemy reserved name: Changed `metadata` → `job_metadata`
- ✅ Email validator dependency: Removed `EmailStr`, using `str`
- ✅ Workflow startup: Successfully running on port 5000

### Current Limitations
- Docker/Kubernetes configs are reference-only (Replit doesn't support Docker runtime)
- Mock connectors used by default (Adzuna is real but requires API keys)
- Frontend is Next.js but workflow is API-only (frontend can be added as separate workflow)

## Deployment

### Replit (Current)
- API Server workflow configured on port 5000
- PostgreSQL database integrated
- Environment secrets managed by Replit

### Docker Compose (Local/Staging)
```bash
cd docker
docker-compose up -d
```

### Kubernetes (Production)
```bash
helm install jobfinder-pro ./k8s/helm -f values.yaml
```

## Monitoring and Observability

### Structured Logging
All logs are in JSON format:
```json
{
  "timestamp": "2025-10-27T12:00:00+00:00",
  "level": "INFO",
  "message": "Resume parsed successfully",
  "user_id": 123,
  "resume_id": 456
}
```

### Prometheus Metrics
Available at `/metrics`:
- `http_requests_total`: Total HTTP requests
- `http_request_duration_seconds`: Request latency histogram
- `resume_parsing_duration_seconds`: Resume parsing time
- `job_matching_duration_seconds`: Matching computation time

## CLI Utilities

```bash
# Create admin user
python scripts/cli.py create-admin --email admin@example.com

# Database statistics
python scripts/cli.py stats

# Cleanup old jobs
python scripts/cli.py cleanup-old-jobs --days 30

# Reset user password
python scripts/cli.py reset-password --email user@example.com
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:
- Code style and conventions
- Testing requirements
- Pull request process
- Development workflow

## Support

For issues or questions:
- Check documentation in README.md
- Review CONTRIBUTING.md for development guidelines
- Check GitHub issues for known problems

---

**Last Updated**: 2025-10-27
**Status**: ✅ Backend operational, database working, API routes active
