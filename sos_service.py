import random
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.config import settings
from app.models.sos import SOSAlert
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.sos import SOSCreate, SOSUpdate
from app.services.notification_service import NotificationService

class SOSService:
    @staticmethod
    def generate_reference_id(db: Session) -> str:
        while True:
            rand_num = random.randint(100000, 999999)
            ref_id = f"SOS-2026-{rand_num}"
            existing = db.query(SOSAlert).filter(SOSAlert.reference_id == ref_id).first()
            if not existing:
                return ref_id

    @staticmethod
    def create_sos(
        db: Session,
        sos_data: SOSCreate,
        user: Optional[User] = None,
        ip_address: Optional[str] = None
    ) -> SOSAlert:
        ref_id = SOSService.generate_reference_id(db)

        user_name = sos_data.user_name or (user.full_name if user else "Citizen in Distress")
        user_phone = sos_data.user_phone or (user.phone if user else "Not Provided")

        sos = SOSAlert(
            reference_id=ref_id,
            user_id=user.id if user else None,
            user_name=user_name,
            user_phone=user_phone,
            latitude=sos_data.latitude,
            longitude=sos_data.longitude,
            address=sos_data.address or "Captured GPS Coordinates",
            status="ALERT_SENT",
            dispatched_unit=None,
            notes=sos_data.notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(sos)

        # Audit log
        audit = AuditLog(
            user_id=user.id if user else None,
            user_email=user.email if user else "sos-citizen",
            action="TRIGGER_SOS",
            target_type="sos",
            target_id=ref_id,
            details=f"SOS triggered at ({sos_data.latitude}, {sos_data.longitude}). Emergency location shared.",
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        db.refresh(sos)

        # High-priority alert to Authority Command Center
        NotificationService.create_notification(
            db=db,
            title="CRITICAL: Emergency SOS Triggered!",
            message=f"SOS alert {ref_id} activated at {sos.address} by {user_name} (Phone: {user_phone}). Immediate dispatch required.",
            target_role="authority",
            notification_type="sos_alert",
            incident_ref=ref_id
        )

        return sos

    @staticmethod
    def update_status(
        db: Session,
        sos_id: int,
        update_data: SOSUpdate,
        authority_user: User,
        ip_address: Optional[str] = None
    ) -> Optional[SOSAlert]:
        sos = db.query(SOSAlert).filter(SOSAlert.id == sos_id).first()
        if not sos:
            return None

        old_status = sos.status
        sos.status = update_data.status
        if update_data.dispatched_unit:
            sos.dispatched_unit = update_data.dispatched_unit
        if update_data.notes:
            sos.notes = update_data.notes
        sos.updated_at = datetime.utcnow()

        audit = AuditLog(
            user_id=authority_user.id,
            user_email=authority_user.email,
            action="UPDATE_SOS",
            target_type="sos",
            target_id=sos.reference_id,
            details=f"Status changed from {old_status} to {update_data.status}. Unit: {sos.dispatched_unit}",
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        db.refresh(sos)

        if sos.user_id:
            NotificationService.create_notification(
                db=db,
                title=f"SOS Response Update: {sos.reference_id}",
                message=f"Status: {sos.status}. Dispatched Unit: {sos.dispatched_unit or 'Command Patrol'}.",
                target_role="citizen",
                user_id=sos.user_id,
                notification_type="sos_alert",
                incident_ref=sos.reference_id
            )

        return sos

    @staticmethod
    def get_all(db: Session, active_only: bool = False) -> List[SOSAlert]:
        query = db.query(SOSAlert)
        if active_only:
            query = query.filter(SOSAlert.status != "RESOLVED")
        return query.order_by(desc(SOSAlert.created_at)).all()
