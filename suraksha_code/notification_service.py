from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.notification import Notification

class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        title: str,
        message: str,
        target_role: str = "citizen",
        user_id: Optional[int] = None,
        notification_type: str = "incident_update",
        incident_ref: Optional[str] = None
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            target_role=target_role,
            title=title,
            message=message,
            type=notification_type,
            incident_reference_id=incident_ref,
            is_read=False
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: Optional[int],
        role: str,
        limit: int = 30
    ) -> List[Notification]:
        query = db.query(Notification)
        if user_id:
            # User specific OR role-based broadcasts
            query = query.filter(
                (Notification.user_id == user_id) | 
                (Notification.target_role == role) |
                (Notification.target_role == "all")
            )
        else:
            query = query.filter(
                (Notification.target_role == role) |
                (Notification.target_role == "all")
            )
        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    @staticmethod
    def mark_all_read(db: Session, user_id: Optional[int], role: str):
        query = db.query(Notification)
        if user_id:
            query = query.filter((Notification.user_id == user_id) | (Notification.target_role == role))
        else:
            query = query.filter(Notification.target_role == role)
        query.update({Notification.is_read: True}, synchronize_session=False)
        db.commit()
