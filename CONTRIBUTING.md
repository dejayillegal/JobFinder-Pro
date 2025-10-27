# Contributing to JobFinder Pro

Thank you for your interest in contributing to JobFinder Pro! This document provides guidelines and instructions for contributing to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive environment for all contributors. Please treat everyone with respect and professionalism.

### Expected Behavior
- Use welcoming and inclusive language
- Respect differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other contributors

### Unacceptable Behavior
- Harassment or discriminatory language
- Personal attacks or trolling
- Publishing private information without permission
- Other conduct inappropriate in a professional setting

## Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/jobfinder-pro.git
   cd jobfinder-pro
   ```

2. **Set up development environment**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   
   # Install pre-commit hooks
   pre-commit install
   
   # Set up database
   alembic upgrade head
   
   # Install frontend dependencies
   cd frontend && npm install
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### 1. Make Your Changes

- Keep changes focused on a single feature or bug fix
- Write clear, self-documenting code
- Add comments for complex logic
- Update documentation as needed

### 2. Test Your Changes

```bash
# Run Python tests
pytest

# Run with coverage
pytest --cov=api --cov-report=html

# Run frontend tests (if applicable)
cd frontend && npm test
```

### 3. Lint and Format

```bash
# Python (Black, isort, flake8)
black api/
isort api/
flake8 api/

# TypeScript/JavaScript (ESLint, Prettier)
cd frontend
npm run lint
npm run format
```

### 4. Commit Your Changes

Use conventional commits format:

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```bash
git commit -m "feat(matcher): add location-based scoring

Implemented location scoring algorithm that prioritizes
Bangalore and Remote positions for India-focused matching.

Closes #123"
```

## Code Style

### Python

We follow PEP 8 with these specifics:

```python
# Good
def calculate_match_score(
    skills: list[str],
    experience: int,
    location: str
) -> float:
    """
    Calculate job match score.
    
    Args:
        skills: List of candidate skills
        experience: Years of experience
        location: Preferred location
    
    Returns:
        Match score from 0-100
    """
    # Implementation
    pass

# Use type hints
from typing import Optional

def parse_resume(file_path: str) -> Optional[dict]:
    pass

# Use dataclasses or Pydantic for data models
from pydantic import BaseModel

class JobMatch(BaseModel):
    job_id: int
    score: float
    explanation: str
```

### TypeScript/React

```typescript
// Good
interface JobMatchProps {
  jobId: number;
  score: number;
  title: string;
}

const JobMatchCard: React.FC<JobMatchProps> = ({ 
  jobId, 
  score, 
  title 
}) => {
  // Component implementation
};

// Use functional components with hooks
import { useState, useEffect } from 'react';

// Prefer named exports
export { JobMatchCard };
```

### File Organization

```
api/app/
├── core/          # Core utilities (database, config, security)
├── models/        # Database models
├── services/      # Business logic
├── connectors/    # External API integrations
├── routes/        # API endpoints
└── tasks.py       # Background tasks
```

## Testing

### Writing Tests

```python
# tests/test_matcher.py
import pytest
from api.app.services.matcher import calculate_match_score

def test_exact_skill_match():
    """Test matching when all skills match exactly."""
    candidate_skills = ["Python", "Django", "PostgreSQL"]
    job_skills = ["Python", "Django", "PostgreSQL"]
    
    score = calculate_match_score(
        candidate_skills=candidate_skills,
        job_skills=job_skills
    )
    
    assert score == 100.0

def test_partial_skill_match():
    """Test matching with partial skill overlap."""
    candidate_skills = ["Python", "Django"]
    job_skills = ["Python", "Django", "React", "AWS"]
    
    score = calculate_match_score(
        candidate_skills=candidate_skills,
        job_skills=job_skills
    )
    
    assert 40.0 < score < 60.0  # Approximately 50% match

@pytest.fixture
def sample_resume_data():
    """Fixture providing sample resume data."""
    return {
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "experience": 5,
        "location": "Bangalore"
    }
```

### Test Coverage

- Aim for >80% code coverage
- Write tests for edge cases
- Test error handling
- Mock external API calls

## Pull Request Process

### Before Submitting

1. ✅ Tests pass locally
2. ✅ Code is linted and formatted
3. ✅ Documentation is updated
4. ✅ Commit messages follow conventions
5. ✅ Branch is up to date with main

### Submitting a PR

1. **Create descriptive PR title**
   ```
   feat(connector): add Indeed API integration
   ```

2. **Fill out PR template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [x] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - Describe testing performed
   - Include test results
   
   ## Checklist
   - [x] Code follows style guidelines
   - [x] Tests added/updated
   - [x] Documentation updated
   - [x] No breaking changes
   ```

3. **Request review**
   - Tag relevant maintainers
   - Respond to feedback promptly
   - Make requested changes

### Review Process

- At least one approval required
- All CI checks must pass
- No unresolved comments
- Squash and merge when approved

## Reporting Bugs

### Before Reporting

1. Check existing issues
2. Verify bug on latest version
3. Collect reproduction steps

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the issue

**To Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What should happen

**Actual behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.11.5]
- Browser: [e.g., Chrome 120]

**Additional context**
Logs, screenshots, etc.
```

## Suggesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Description of the problem

**Describe the solution you'd like**
Clear description of desired functionality

**Describe alternatives you've considered**
Other approaches you've thought about

**Additional context**
Mockups, examples, use cases
```

## Development Tips

### Database Migrations

```bash
# Create new migration
alembic revision -m "add user preferences table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Debugging

```python
# Use structured logging
import logging
logger = logging.getLogger(__name__)

logger.info("Processing resume", extra={
    "user_id": user.id,
    "filename": filename
})

# Use debugger
import pdb; pdb.set_trace()
```

### Performance Testing

```bash
# Load testing with locust
locust -f tests/load_test.py

# Profile Python code
python -m cProfile -o profile.stats api/main.py
```

## Questions?

- Open a discussion on GitHub
- Check documentation
- Review existing issues

Thank you for contributing! 🎉
