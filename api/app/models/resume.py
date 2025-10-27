"""Resume model for storing parsed resume data."""
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Resume(Base):
    """Resume model storing parsed resume information."""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    
    raw_text = Column(Text, nullable=True)
    
    skills = Column(JSON, default=list)
    years_experience = Column(Integer, nullable=True)
    current_role = Column(String, nullable=True)
    locations_preferred = Column(JSON, default=list)
    education = Column(JSON, default=list)
    
    parsed_data = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="resumes")
