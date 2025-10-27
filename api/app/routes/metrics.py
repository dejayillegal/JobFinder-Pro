"""Prometheus metrics endpoint."""
from fastapi import APIRouter, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

router = APIRouter(tags=["Metrics"])

request_count = Counter(
    "jobfinder_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

request_duration = Histogram(
    "jobfinder_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

resumes_processed = Counter(
    "jobfinder_resumes_processed_total",
    "Total resumes processed"
)

jobs_matched = Counter(
    "jobfinder_jobs_matched_total",
    "Total job matches created"
)


@router.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
