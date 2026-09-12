from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.config import settings
from app.database import get_db
from app.models.incident import Incident
from app.models.sos import SOSAlert
from app.models.user import User
from app.schemas.dashboard import CitizenDashboardStats, AuthorityDashboardStats
from app.schemas.incident import IncidentPublicSafeOut, IncidentOut
from app.schemas.sos import SOSOut
from app.auth.jwt import get_current_user_optional, require_authority

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/citizen", response_model=CitizenDashboardStats)
def get_citizen_dashboard(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    active_incidents = (
        db.query(Incident)
        .filter(Incident.status != "Resolved")
        .order_by(desc(Incident.created_at))
        .limit(6)
        .all()
    )

    public_incidents = []
    for inc in active_incidents:
        public_incidents.append(IncidentPublicSafeOut(
            id=inc.id,
            reference_id=inc.reference_id,
            title=inc.title,
            category=inc.category,
            severity=inc.severity,
            status=inc.status,
            latitude=inc.public_safe_latitude or inc.latitude,
            longitude=inc.public_safe_longitude or inc.longitude,
            address=inc.address,
            landmark=inc.landmark,
            created_at=inc.created_at,
            updated_at=inc.updated_at,
            evidence_count=len(inc.evidence)
        ))

    my_count = 0
    if current_user:
        my_count = db.query(Incident).filter(Incident.reported_by_id == current_user.id).count()

    total_active = len(active_incidents)
    if total_active == 0:
        msg = "All clear. No active incidents reported in this zone today."
        status_banner = "Area Normal & Monitored"
    elif total_active <= 3:
        msg = f"{total_active} active incidents reported nearby. Response units have been dispatched."
        status_banner = "Area Monitored with Normal Response Activity"
    else:
        msg = f"{total_active} active incidents in this sector. Stay informed and follow authority guidance."
        status_banner = "Elevated Response Activity in Sector"

    return CitizenDashboardStats(
        monitored_status=status_banner,
        safety_message=msg,
        nearby_incidents_count=total_active,
        active_incidents_nearby=public_incidents,
        my_reports_count=my_count,
        emergency_services=settings.EMERGENCY_SERVICES
    )

@router.get("/authority", response_model=AuthorityDashboardStats)
def get_authority_dashboard(
    authority_user: User = Depends(require_authority),
    db: Session = Depends(get_db)
):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    total_today = db.query(Incident).filter(Incident.created_at >= today_start).count()
    active_count = db.query(Incident).filter(Incident.status != "Resolved", Incident.status != "Rejected").count()
    sos_active = db.query(SOSAlert).filter(SOSAlert.status != "RESOLVED").count()
    pending_verify = db.query(Incident).filter(Incident.verification_status == "Under Review").count()

    critical_count = db.query(Incident).filter(Incident.severity == "Critical", Incident.status != "Resolved").count()
    high_count = db.query(Incident).filter(Incident.severity == "High", Incident.status != "Resolved").count()
    moderate_count = db.query(Incident).filter(Incident.severity == "Moderate", Incident.status != "Resolved").count()
    resolved_count = db.query(Incident).filter(Incident.status == "Resolved").count()

    cat_counts = (
        db.query(Incident.category, func.count(Incident.id))
        .group_by(Incident.category)
        .all()
    )
    cat_dict = {cat: count for cat, count in cat_counts}

    recent_sos_raw = db.query(SOSAlert).order_by(desc(SOSAlert.created_at)).limit(5).all()
    recent_sos = []
    for s in recent_sos_raw:
        o = SOSOut.model_validate(s)
        o.emergency_services = settings.EMERGENCY_SERVICES
        recent_sos.append(o)

    recent_incidents = (
        db.query(Incident)
        .order_by(desc(Incident.created_at))
        .limit(6)
        .all()
    )

    return AuthorityDashboardStats(
        total_incidents_today=total_today,
        active_incidents=active_count,
        sos_alerts_active=sos_active,
        pending_verification=pending_verify,
        critical_incidents=critical_count,
        high_incidents=high_count,
        moderate_incidents=moderate_count,
        resolved_incidents=resolved_count,
        category_breakdown=cat_dict,
        recent_sos_alerts=recent_sos,
        recent_incidents=[IncidentOut.model_validate(i) for i in recent_incidents]
    )
