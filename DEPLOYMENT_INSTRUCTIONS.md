
# Local Deployment Instructions

## Running JobFinder Pro in Separate Terminals

This guide helps you run the application components in different terminal windows for easier debugging and monitoring.

### Prerequisites

Make sure you have completed the initial setup:
```bash
# Copy environment file
cp .env.example .env

# Edit .env with your configuration
# Set DATABASE_URL, REDIS_URL, SECRET_KEY, etc.
```

### Step 1: Start Database Services (Terminal 1)

```bash
chmod +x scripts/start_database.sh
./scripts/start_database.sh
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)

**Keep this terminal open** - it maintains the database services.

### Step 2: Start Backend API Server (Terminal 2)

```bash
chmod +x scripts/start_backend.sh
./scripts/start_backend.sh
```

This will:
- Install Python dependencies
- Download spaCy model (if needed)
- Run database migrations
- Start FastAPI server on port 8000

Access:
- API Docs: http://0.0.0.0:8000/docs
- Health Check: http://0.0.0.0:8000/api/health

### Step 3: Start Celery Worker (Terminal 3)

```bash
chmod +x scripts/start_celery.sh
./scripts/start_celery.sh
```

This will start the background job processor for resume parsing and job matching.

### Step 4: Start Frontend (Terminal 4)

```bash
chmod +x scripts/start_frontend.sh
./scripts/start_frontend.sh
```

This will:
- Install Node.js dependencies
- Start Next.js development server on port 5000

Access:
- Frontend: http://0.0.0.0:5000

### Stopping Services

To stop all services:
1. Press `Ctrl+C` in each terminal
2. Services will shut down gracefully

### Troubleshooting

#### spaCy Download Error

If you encounter the 404 error with spaCy, run this manually:

```bash
# Upgrade spaCy first
pip install -U spacy

# Then download the model
python -m spacy download en_core_web_sm
```

Or install directly from a specific version:
```bash
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

#### PostgreSQL Not Running

**macOS:**
```bash
brew services start postgresql@15
```

**Linux:**
```bash
sudo systemctl start postgresql
```

#### Redis Not Running

**macOS:**
```bash
brew services start redis
```

**Linux:**
```bash
sudo systemctl start redis-server
```

### Quick Start (Single Command)

If you prefer to run everything from one script:
```bash
./scripts/dev_start.sh
```

This runs all services in the background, but separate terminals give you better visibility and control.
