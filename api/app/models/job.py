"""Job-related models for storing job listings and matches."""
from sqlalchemy import Column, Integer, String, Text, Float, JSON, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Job(Base):
    """Job listing from external sources."""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=False)
    source = Column(String, nullable=False)
    
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    excerpt = Column(String, nullable=True)
    
    url = Column(String, nullable=False)
    posted_date = Column(DateTime(timezone=True), nullable=True)
    
    required_skills = Column(JSON, default=list)
    seniority_level = Column(String, nullable=True)
    
    job_metadata = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    matches = relationship("JobMatch", back_populates="job")


class JobMatch(Base):
    """Match between a user's resume and a job."""
    __tablename__ = "job_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    
    match_score = Column(Float, nullable=False)
    skills_score = Column(Float, default=0.0)
    seniority_score = Column(Float, default=0.0)
    location_score = Column(Float, default=0.0)
    
    top_factors = Column(JSON, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="job_matches")
    job = relationship("Job", back_populates="matches")
    
    __table_args__ = (
        Index('idx_user_score', 'user_id', 'match_score'),
    )


class ProcessingJob(Base):
    """Background processing job tracking."""
    __tablename__ = "processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    
    status = Column(String, default="pending")
    progress = Column(Integer, default=0)
    
    result = Column(JSON, default=dict)
    error = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
