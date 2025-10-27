
#!/usr/bin/env python3
"""
Validate that all required services and configurations are ready.
"""

import sys
import os
from pathlib import Path


def check_environment():
    """Check environment variables."""
    print("Checking environment variables...")
    
    required_vars = [
        "DATABASE_URL",
        "REDIS_URL",
        "SECRET_KEY"
    ]
    
    optional_vars = [
        "ADZUNA_APP_ID",
        "ADZUNA_API_KEY"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
            print(f"  ❌ {var} is not set")
        else:
            print(f"  ✅ {var} is set")
    
    for var in optional_vars:
        if not os.getenv(var):
            print(f"  ⚠️  {var} is not set (using mock data)")
        else:
            print(f"  ✅ {var} is set")
    
    return len(missing) == 0


def check_database():
    """Check database connection."""
    print("\nChecking database connection...")
    
    try:
        from api.app.core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("  ✅ Database connection successful")
            return True
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return False


def check_redis():
    """Check Redis connection."""
    print("\nChecking Redis connection...")
    
    try:
        import redis
        from api.app.core.config import settings
        
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        print("  ✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"  ⚠️  Redis connection failed: {e}")
        print("     (Celery tasks will not work)")
        return True  # Don't fail tests for Redis


def check_dependencies():
    """Check Python dependencies."""
    print("\nChecking Python dependencies...")
    
    required_packages = [
        "fastapi",
        "sqlalchemy",
        "pydantic",
        "pytest",
        "httpx"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package} installed")
        except ImportError:
            print(f"  ❌ {package} not installed")
            missing.append(package)
    
    return len(missing) == 0


def main():
    """Run all validation checks."""
    print("=" * 80)
    print("JobFinder Pro - Setup Validation")
    print("=" * 80)
    
    checks = [
        ("Environment Variables", check_environment),
        ("Python Dependencies", check_dependencies),
        ("Database Connection", check_database),
        ("Redis Connection", check_redis)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Error during {name} check: {e}")
            results.append(False)
    
    print("\n" + "=" * 80)
    if all(results):
        print("✅ All validation checks passed!")
        print("=" * 80)
        print("\nYou can now run the tests with: pytest tests/")
        return 0
    else:
        print("❌ Some validation checks failed!")
        print("=" * 80)
        print("\nPlease fix the issues above before running tests.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
