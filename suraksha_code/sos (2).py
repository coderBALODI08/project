from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.sos import SOSAlert
from app.schemas.sos import SOSCreate, SOSUpdate, SOSOut
from app.auth.jwt import get_current_user_optional, require_authority
from app.services.sos_service import SOSService

router = APIRouter(prefix="/sos", tags=["SOS Emergency"])

@router.get("/helplines")
def get_helplines():
    return {
        "disclaimer": "For immediate life-threatening emergencies, contact the appropriate official emergency service directly.",
        "services": settings.EMERGENCY_SERVICES
    }

@router.post("", response_model=SOSOut, status_code=status.HTTP_201_CREATED)
def trigger_sos(
    sos_in: SOSCreate,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    sos = SOSService.create_sos(
        db=db,
        sos_data=sos_in,
        user=current_user,
        ip_address=client_ip
    )
    result = SOSOut.model_validate(sos)
    result.emergency_services = settings.EMERGENCY_SERVICES
    return result

@router.get("", response_model=List[SOSOut])
def list_sos_alerts(
    active_only: bool = False,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    if current_user and current_user.role == "authority":
        alerts = SOSService.get_all(db=db, active_only=active_only)
    elif current_user:
        alerts = db.query(SOSAlert).filter(SOSAlert.user_id == current_user.id).order_by(SOSAlert.created_at.desc()).all()
    else:
        alerts = []
    
    out_list = []
    for a in alerts:
        o = SOSOut.model_validate(a)
        o.emergency_services = settings.EMERGENCY_SERVICES
        out_list.append(o)
    return out_list

@router.get("/{id_or_ref}", response_model=SOSOut)
def get_sos_detail(
    id_or_ref: str,
    db: Session = Depends(get_db)
):
    if id_or_ref.isdigit():
        sos = db.query(SOSAlert).filter(SOSAlert.id == int(id_or_ref)).first()
    else:
        sos = db.query(SOSAlert).filter(SOSAlert.reference_id == id_or_ref).first()

    if not sos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SOS alert '{id_or_ref}' not found."
        )
    result = SOSOut.model_validate(sos)
    result.emergency_services = settings.EMERGENCY_SERVICES
    return result

@router.put("/{sos_id}/status", response_model=SOSOut)
def update_sos_status(
    sos_id: int,
    update_in: SOSUpdate,
    request: Request,
    authority_user: User = Depends(require_authority),
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    updated = SOSService.update_status(
        db=db,
        sos_id=sos_id,
        update_data=update_in,
        authority_user=authority_user,
        ip_address=client_ip
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SOS alert not found.")
    result = SOSOut.model_validate(updated)
    result.emergency_services = settings.EMERGENCY_SERVICES
    return result
