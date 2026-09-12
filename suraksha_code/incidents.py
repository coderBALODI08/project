from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.incident import Incident
from app.models.evidence import IncidentEvidence
from app.models.user import User
from app.schemas.incident import (
    IncidentCreate,
    IncidentOut,
    IncidentPublicSafeOut,
    IncidentUpdateStatus,
    IncidentAssign,
    EvidenceOut
)
from app.auth.jwt import get_current_user_optional, get_current_user, require_authority
from app.services.incident_service import IncidentService
from app.utils.file_handler import save_evidence_file

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=List[IncidentOut])
def list_incidents(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    verification_status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return IncidentService.get_incidents(
        db=db,
        category=category,
        severity=severity,
        status=status,
        verification_status=verification_status,
        search=search,
        limit=limit
    )

@router.get("/my-reports", response_model=List[IncidentOut])
def get_my_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return IncidentService.get_incidents(db=db, user_id=current_user.id)

@router.get("/{id_or_ref}", response_model=IncidentOut)
def get_incident_detail(
    id_or_ref: str,
    db: Session = Depends(get_db)
):
    query = db.query(Incident)
    if id_or_ref.isdigit():
        incident = query.filter(Incident.id == int(id_or_ref)).first()
    else:
        incident = query.filter(Incident.reference_id == id_or_ref).first()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident report '{id_or_ref}' was not found in our records."
        )
    return incident

@router.post("", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def create_incident(
    incident_in: IncidentCreate,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    return IncidentService.create_incident(
        db=db,
        incident_data=incident_in,
        user=current_user,
        ip_address=client_ip
    )

@router.post("/{incident_id}/evidence", response_model=EvidenceOut)
def upload_evidence(
    incident_id: int,
    file: UploadFile = File(...),
    caption: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found to attach evidence."
        )

    saved_meta = save_evidence_file(file, incident_id)
    evidence = IncidentEvidence(
        incident_id=incident_id,
        file_path=saved_meta["file_path"],
        file_name=saved_meta["file_name"],
        file_type=saved_meta["file_type"],
        file_size=saved_meta["file_size"],
        caption=caption
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence

@router.put("/{incident_id}/status", response_model=IncidentOut)
def update_status(
    incident_id: int,
    status_update: IncidentUpdateStatus,
    request: Request,
    authority_user: User = Depends(require_authority),
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    updated = IncidentService.update_status(
        db=db,
        incident_id=incident_id,
        update_data=status_update,
        authority_user=authority_user,
        ip_address=client_ip
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found.")
    return updated

@router.put("/{incident_id}/assign", response_model=IncidentOut)
def assign_incident(
    incident_id: int,
    assign_data: IncidentAssign,
    request: Request,
    authority_user: User = Depends(require_authority),
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    updated = IncidentService.assign_incident(
        db=db,
        incident_id=incident_id,
        assign_data=assign_data,
        authority_user=authority_user,
        ip_address=client_ip
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found.")
    return updated
