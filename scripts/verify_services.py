
#!/usr/bin/env python3
"""Verify all services are running and connected properly."""

import sys
import os
import requests
import psycopg2
import redis

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.app.core.config import settings

def check_database():
    """Check PostgreSQL connection."""
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        conn.close()
        print("✅ Database: Connected")
        return True
    except Exception as e:
        print(f"❌ Database: Failed - {e}")
        return False

def check_redis():
    """Check Redis connection."""
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        print("✅ Redis: Connected")
        return True
    except Exception as e:
        print(f"❌ Redis: Failed - {e}")
        return False

def check_api():
    """Check API server."""
    try:
        response = requests.get(f"http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Server: Running on port 8000")
            return True
        else:
            print(f"❌ API Server: Returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Server: Not accessible - {e}")
        return False

def check_frontend():
    """Check Frontend server."""
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend: Running on port 5000")
            return True
        else:
            print(f"⚠️  Frontend: Returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend: Not accessible - {e}")
        return False

def check_api_credentials():
    """Check if API credentials are configured."""
    try:
        if settings.ADZUNA_APP_ID and settings.ADZUNA_APP_KEY:
            print("✅ API Credentials: Adzuna configured")
            return True
        else:
            print("⚠️  API Credentials: Using mock data (run scripts/setup_apis.py)")
            return False
    except Exception as e:
        print(f"❌ API Credentials: Error - {e}")
        return False

def main():
    print("🔍 Verifying JobFinder Pro Services...\n")
    
    results = {
        "Database": check_database(),
        "Redis": check_redis(),
        "API Server": check_api(),
        "Frontend": check_frontend(),
        "API Credentials": check_api_credentials()
    }
    
    print("\n" + "="*50)
    passed = sum(results.values())
    total = len(results)
    
    if passed == total:
        print(f"✅ All services operational ({passed}/{total})")
        print("\n🎉 JobFinder Pro is ready!")
        print(f"   Frontend: http://localhost:5000")
        print(f"   API Docs: http://localhost:8000/docs")
        return 0
    else:
        print(f"⚠️  Some services need attention ({passed}/{total} operational)")
        print("\nPlease start missing services:")
        if not results["Database"]:
            print("  - PostgreSQL: brew services start postgresql@15")
        if not results["Redis"]:
            print("  - Redis: brew services start redis")
        if not results["API Server"]:
            print("  - API Server: Start 'API Server' workflow")
        if not results["Frontend"]:
            print("  - Frontend: Start 'Frontend' workflow")
        return 1

if __name__ == "__main__":
    sys.exit(main())
