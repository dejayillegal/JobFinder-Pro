
#!/bin/bash

echo "🛑 Stopping JobFinder Pro services..."

if [ -f .production_pids ]; then
    PIDS=$(cat .production_pids)
    echo "Killing processes: $PIDS"
    kill $PIDS 2>/dev/null || echo "Some processes already stopped"
    rm .production_pids
    echo "✅ All services stopped"
else
    echo "⚠️  No .production_pids file found"
    echo "Attempting to find and stop services manually..."
    
    # Kill uvicorn processes
    pkill -f "uvicorn api.main:app" || true
    
    # Kill celery processes
    pkill -f "celery -A api.app.celery_app" || true
    
    # Kill npm processes in frontend directory
    pkill -f "npm run start" || true
    
    echo "✅ Cleanup complete"
fi
