# Assigned to: Raj (Rajendra Brahmbhatt)
# Phase: 3 (B3.4)
#
# Top-level messaging endpoint for fetching all conversation threads
# for the current user (not scoped to a single listing).

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.message_service import get_user_threads

router = APIRouter()


@router.get("/threads")
def list_threads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all message threads for the current user, grouped by listing."""
    return {"threads": get_user_threads(db, current_user.id)}
