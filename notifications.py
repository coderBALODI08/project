from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.notification import NotificationOut
from app.auth.jwt import get_current_user_optional
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=List[NotificationOut])
def get_notifications(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None
    role = current_user.role if current_user else "citizen"
    return NotificationService.get_user_notifications(db=db, user_id=user_id, role=role)

@router.post("/read-all")
def mark_notifications_read(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None
    role = current_user.role if current_user else "citizen"
    NotificationService.mark_all_read(db=db, user_id=user_id, role=role)
    return {"message": "Notifications marked as read."}
