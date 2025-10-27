"""Admin routes for user management and reindexing."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from ..core.database import get_db
from ..core.security import get_current_admin_user
from ..models import User
from ..tasks import reindex_user_task

router = APIRouter(prefix="/admin", tags=["Admin"])


class UserInfo(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    is_admin: bool
    
    class Config:
        from_attributes = True


class ReindexRequest(BaseModel):
    user_id: int


class ReindexResponse(BaseModel):
    message: str
    user_id: int


@router.get("/users", response_model=List[UserInfo])
def list_users(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List all users (admin only)."""
    users = db.query(User).all()
    return users


@router.post("/reindex", response_model=ReindexResponse)
def reindex_user(
    request: ReindexRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Re-run job matching for a user (admin only)."""
    user = db.query(User).filter(User.id == request.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    reindex_user_task.delay(request.user_id)
    
    return ReindexResponse(
        message=f"Reindexing started for user {user.email}",
        user_id=user.id
    )
