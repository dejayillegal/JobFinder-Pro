"""Resume upload and processing routes."""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import os
import uuid
from pathlib import Path
from ..core.database import get_db
from ..core.security import get_current_user
from ..core.config import settings
from ..models import User, Resume, ProcessingJob
from ..tasks import process_resume_task

router = APIRouter(prefix="/resume", tags=["Resume"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class ResumeUploadResponse(BaseModel):
    job_id: str
    message: str
    resume_id: int


class ProcessingStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    result: Optional[dict] = None
    error: Optional[str] = None


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload resume for processing.
    
    Accepts PDF, DOCX, or TXT files.
    Returns a job ID for tracking processing status.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    file_ext = Path(file.filename).suffix.lower().replace('.', '')
    
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.{file_ext}"
    file_path = UPLOAD_DIR / filename
    
    with open(file_path, "wb") as f:
        content = await file.read()
        
        max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        f.write(content)
    
    resume = Resume(
        user_id=current_user.id,
        filename=file.filename,
        file_path=str(file_path)
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    job_id = f"resume_{current_user.id}_{resume.id}_{file_id}"
    
    processing_job = ProcessingJob(
        job_id=job_id,
        user_id=current_user.id,
        resume_id=resume.id,
        status="pending",
        progress=0
    )
    db.add(processing_job)
    db.commit()
    
    process_resume_task.delay(job_id, current_user.id, str(file_path))
    
    return ResumeUploadResponse(
        job_id=job_id,
        message="Resume upload accepted. Processing started.",
        resume_id=resume.id
    )


@router.get("/status/{job_id}", response_model=ProcessingStatus)
def get_processing_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get processing status for a resume upload job."""
    processing_job = db.query(ProcessingJob).filter(
        ProcessingJob.job_id == job_id,
        ProcessingJob.user_id == current_user.id
    ).first()
    
    if not processing_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processing job not found"
        )
    
    return ProcessingStatus(
        job_id=processing_job.job_id,
        status=processing_job.status,
        progress=processing_job.progress,
        result=processing_job.result,
        error=processing_job.error
    )
