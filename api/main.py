"""
JobFinder Pro - Main FastAPI application
Production-grade resume-driven job matching platform
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import logging
from .app.core.config import settings
from .app.core.logging import logger
from .app.core.database import Base, engine
from .app.routes import auth, resume, matches, admin, metrics

Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="JobFinder Pro API",
    description="Resume-driven job matching platform for India",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEV_MODE else None,
    redoc_url="/api/redoc" if settings.DEV_MODE else None
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing."""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    logger.info(
        "Request processed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": process_time
        }
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


app.include_router(auth.router, prefix="/api")
app.include_router(resume.router, prefix="/api")
app.include_router(matches.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")


@app.get("/")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
def root(request: Request):
    """Root endpoint."""
    return {
        "name": "JobFinder Pro API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEV_MODE
    )
