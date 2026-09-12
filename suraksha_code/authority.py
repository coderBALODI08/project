from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.user import User
from app.models.incident import Incident
from app.models.audit import AuditLog
from app.schemas.user import UserOut
from app.schemas.incident import IncidentOut, IncidentUpdateStatus
from app.auth.jwt import require_authority
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/authority", tags=["Authority Operations"])

class ActionReason(BaseModel):
    reason: Optional[str] = None

@router.get("/officers", response_model=List[UserOut])
def get_available_officers(
    authority_user: User = Depends(require_authority),
    db: Session = Depends(get_db)
):
    return db.query(User).filter(User.role == "authority", User.is_active == True).all()

@router.get("/audit-logs")
def get_audit_logs(
    limit: int = 50,
    authority_user: User = Depends(require_authority),
    db: Session = Depends(get_db)
):
    logs = db.query(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit).all()
    return [
        {
            "id": l.id,
            "user_email": l.user_email,
            "action": l.action,
            "target_type": l.target_type,
            "target_id": l.target_id,
            "details": l.details,
            "ip_address": l.ip_address,
            "timestamp": l.timestamp.isoformat()
        }
        for l in logs
    ]

@router.post("/verify/{incident_id}", response_model=IncidentOut)
def quick_verify(
    incident_id: int,
    body: ActionReason,
    request: Request,
    authority_user: User = Depends(require_authority),
    db: Session = Depends(get_db)
):
    note = body.reason or "Report verified via official telemetry and preliminary eyewitness check."
    return IncidentService.update_status(
        db=db,
        incident_id=incident_id,
        update_data=IncidentUpdateStatus(
            status="Under Verification",
            verification_status="Verified",
            comment=note
        ),
        authority_user=authority_user,
        ip_address=request.client.host if request.client else None
    )

@router.post("/reject/{incident_id}", response_model=IncidentOut)
def quick_reject(
    incident_id: int,
    body: ActionReason,
    request: Request,
    authority_user: User = Depends(require_authority),
    db: Session = Depends(get_db)
):
    note = body.reason or "Report flagged as inaccurate, duplicate, or unverified by field dispatch."
    return IncidentService.update_status(
        db=db,
        incident_id=incident_id,
        update_data=IncidentUpdateStatus(
            status="Rejected",
            verification_status="Rejected",
            comment=note
        ),
        authority_user=authority_user,
        ip_address=request.client.host if request.client else None
    )
