"""
Celery background tasks for resume processing and job matching.
"""
from typing import Dict, Any, List
import logging
from sqlalchemy.orm import Session
from .celery_app import celery_app
from .core.database import SessionLocal
from .core.config import settings
from .models import User, Resume, Job, JobMatch, ProcessingJob
from .services.resume_parser import ResumeParser
from .services.matcher import JobMatcher
from .services.advanced_matcher import AdvancedJobMatcher
from .services.job_deduplicator import job_deduplicator
from .connectors import (
    AdzunaConnector,
    IndeedConnector,
    JoobleConnector,
    LinkedInConnector,
    NaukriConnector,
    RSSAggregator,
    RapidAPIConnector
)

logger = logging.getLogger(__name__)


def get_all_connectors():
    """Get list of all job connectors including advanced ones."""
    connectors = [
        RSSAggregator(),
        RapidAPIConnector(),
        AdzunaConnector(),
        IndeedConnector()
    ]
    
    if not settings.MOCK_CONNECTORS:
        connectors.extend([
            JoobleConnector(),
            LinkedInConnector(),
            NaukriConnector()
        ])
    
    return connectors


def deduplicate_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate jobs using advanced deduplicator."""
    if settings.ENABLE_JOB_DEDUPLICATION:
        source_priority = ["RapidAPI", "Adzuna", "RSSAggregator", "Indeed", "Jooble", "LinkedIn", "Naukri"]
        return job_deduplicator.deduplicate_jobs(jobs, keep_source_priority=source_priority)
    else:
        seen_urls = set()
        unique_jobs = []
        
        for job in jobs:
            url = job.get("url", "")
            
            if url and url in seen_urls:
                continue
            
            if url:
                seen_urls.add(url)
            
            unique_jobs.append(job)
        
        return unique_jobs


@celery_app.task(bind=True)
def process_resume_task(self, processing_job_id: str, user_id: int, file_path: str):
    """
    Background task to process resume and find matching jobs.
    
    Steps:
    1. Parse resume
    2. Fetch jobs from all connectors in parallel
    3. Compute match scores
    4. Save matches to database
    5. Update processing job status
    """
    db: Session = SessionLocal()
    
    try:
        processing_job = db.query(ProcessingJob).filter(
            ProcessingJob.job_id == processing_job_id
        ).first()
        
        if not processing_job:
            logger.error(f"Processing job {processing_job_id} not found")
            return
        
        processing_job.status = "processing"
        processing_job.progress = 10
        db.commit()
        
        parser = ResumeParser()
        parsed_data = parser.parse_resume(file_path)
        
        if not parsed_data.get("success"):
            processing_job.status = "failed"
            processing_job.error = parsed_data.get("error", "Unknown parsing error")
            db.commit()
            return
        
        resume = db.query(Resume).filter(Resume.id == processing_job.resume_id).first()
        if resume:
            resume.raw_text = parsed_data.get("raw_text", "")
            resume.skills = parsed_data.get("skills", [])
            resume.years_experience = parsed_data.get("years_experience")
            resume.current_role = parsed_data.get("current_role")
            resume.locations_preferred = parsed_data.get("locations_preferred", [])
            resume.parsed_data = parsed_data
            db.commit()
        
        processing_job.progress = 30
        db.commit()
        
        all_jobs = []
        connectors = get_all_connectors()
        
        # Build query from resume data
        skills = parsed_data.get("skills", [])
        current_role = parsed_data.get("current_role", "")
        
        # Determine best query based on resume
        if current_role:
            query = current_role
        elif skills:
            # Use top skills to form query
            primary_skills = skills[:3]
            query = " ".join(primary_skills)
        else:
            query = "Software Engineer"
        
        # Get preferred locations
        locations = parsed_data.get("locations_preferred", ["India"])
        primary_location = locations[0] if locations else "India"
        
        logger.info(f"Searching jobs with query: '{query}' in {primary_location}")
        
        for i, connector in enumerate(connectors):
            try:
                jobs = connector.search_jobs(query=query, location=primary_location, max_results=15)
                all_jobs.extend(jobs)
                
                progress = 30 + int((i + 1) / len(connectors) * 40)
                processing_job.progress = progress
                db.commit()
                
                logger.info(f"Fetched {len(jobs)} jobs from {connector.name}")
            except Exception as e:
                logger.error(f"Error fetching from {connector.name}: {e}")
        
        all_jobs = deduplicate_jobs(all_jobs)
        
        processing_job.progress = 70
        db.commit()
        
        for job_data in all_jobs:
            external_id = f"{job_data['source']}:{job_data['url']}"
            
            existing_job = db.query(Job).filter(Job.external_id == external_id).first()
            
            if not existing_job:
                job = Job(
                    external_id=external_id,
                    source=job_data["source"],
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_data.get("location", ""),
                    description=job_data.get("description", ""),
                    excerpt=job_data.get("excerpt", ""),
                    url=job_data["url"],
                    required_skills=job_data.get("required_skills", []),
                    seniority_level=job_data.get("seniority_level", "")
                )
                db.add(job)
                db.flush()
            else:
                job = existing_job
            
            if settings.USE_ADVANCED_MATCHING:
                matcher = AdvancedJobMatcher(spacy_model=settings.SPACY_MODEL)
            else:
                matcher = JobMatcher()
            
            match_result = matcher.calculate_match_score(parsed_data, job_data)
            
            if match_result["match_score"] >= 30:
                job_match = JobMatch(
                    user_id=user_id,
                    job_id=job.id,
                    resume_id=processing_job.resume_id,
                    match_score=match_result["match_score"],
                    skills_score=match_result["skills_score"],
                    seniority_score=match_result["seniority_score"],
                    location_score=match_result["location_score"],
                    top_factors=match_result["top_factors"]
                )
                db.add(job_match)
        
        db.commit()
        
        processing_job.status = "completed"
        processing_job.progress = 100
        processing_job.result = {
            "total_jobs_found": len(all_jobs),
            "matches_created": db.query(JobMatch).filter(
                JobMatch.user_id == user_id,
                JobMatch.resume_id == processing_job.resume_id
            ).count()
        }
        db.commit()
        
        logger.info(f"Resume processing completed for job {processing_job_id}")
        
    except Exception as e:
        logger.error(f"Error processing resume: {e}")
        if processing_job:
            processing_job.status = "failed"
            processing_job.error = str(e)
            db.commit()
    finally:
        db.close()


@celery_app.task
def reindex_user_task(user_id: int):
    """Re-run job matching for a user's most recent resume."""
    db: Session = SessionLocal()
    
    try:
        resume = db.query(Resume).filter(
            Resume.user_id == user_id
        ).order_by(Resume.created_at.desc()).first()
        
        if not resume:
            logger.warning(f"No resume found for user {user_id}")
            return
        
        db.query(JobMatch).filter(JobMatch.user_id == user_id).delete()
        db.commit()
        
        processing_job = ProcessingJob(
            job_id=f"reindex_{user_id}_{resume.id}",
            user_id=user_id,
            resume_id=resume.id,
            status="pending"
        )
        db.add(processing_job)
        db.commit()
        
        process_resume_task.delay(processing_job.job_id, user_id, resume.file_path)
        
        logger.info(f"Reindexing started for user {user_id}")
    finally:
        db.close()
