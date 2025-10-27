"""Job matches retrieval routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ..core.database import get_db
from ..core.security import get_current_user
from ..models import User, JobMatch, Job

router = APIRouter(prefix="/matches", tags=["Matches"])


class JobMatchResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    excerpt: str
    url: str
    posted_date: Optional[datetime]
    match_score: float
    skills_score: float
    seniority_score: float
    location_score: float
    top_factors: List[dict]
    source: str
    
    class Config:
        from_attributes = True


class MatchesListResponse(BaseModel):
    total: int
    matches: List[JobMatchResponse]


@router.get("/", response_model=MatchesListResponse)
def get_matches(
    min_score: float = Query(30.0, description="Minimum match score"),
    location: Optional[str] = Query(None, description="Filter by location"),
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get job matches for the current user.
    
    Supports filtering by minimum score, location, and source.
    """
    query = db.query(JobMatch, Job).join(Job).filter(
        JobMatch.user_id == current_user.id,
        JobMatch.match_score >= min_score
    )
    
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    
    if source:
        query = query.filter(Job.source.ilike(f"%{source}%"))
    
    total = query.count()
    
    results = query.order_by(desc(JobMatch.match_score)).offset(offset).limit(limit).all()
    
    matches = []
    for job_match, job in results:
        matches.append(JobMatchResponse(
            id=job_match.id,
            title=job.title,
            company=job.company,
            location=job.location,
            excerpt=job.excerpt,
            url=job.url,
            posted_date=job.posted_date,
            match_score=job_match.match_score,
            skills_score=job_match.skills_score,
            seniority_score=job_match.seniority_score,
            location_score=job_match.location_score,
            top_factors=job_match.top_factors,
            source=job.source
        ))
    
    return MatchesListResponse(
        total=total,
        matches=matches
    )


@router.get("/{match_id}", response_model=JobMatchResponse)
def get_match_detail(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific match."""
    result = db.query(JobMatch, Job).join(Job).filter(
        JobMatch.id == match_id,
        JobMatch.user_id == current_user.id
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )
    
    job_match, job = result
    
    return JobMatchResponse(
        id=job_match.id,
        title=job.title,
        company=job.company,
        location=job.location,
        excerpt=job.excerpt,
        url=job.url,
        posted_date=job.posted_date,
        match_score=job_match.match_score,
        skills_score=job_match.skills_score,
        seniority_score=job_match.seniority_score,
        location_score=job_match.location_score,
        top_factors=job_match.top_factors,
        source=job.source
    )
