from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.incident import Incident
from app.models.user import User
from app.auth.jwt import get_current_user_optional
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/map", tags=["Interactive Map"])

# Color and icon specification from product architecture requirements:
# RED = Fire
# ORANGE = Road Accident
# YELLOW = Suspicious Activity
# BLUE = Medical Emergency
# PURPLE = Missing Person
# GREEN = Incident Resolved
# BLACK/DARK = Major/Critical Emergency
CATEGORY_VISUAL_MAP = {
    "Fire": {"color": "#EF4444", "icon": "flame", "badge": "Fire"},
    "Road Accident": {"color": "#F97316", "icon": "car-crash", "badge": "Road Accident"},
    "Suspicious Activity": {"color": "#EAB308", "icon": "alert-triangle", "badge": "Suspicious Activity"},
    "Medical Emergency": {"color": "#3B82F6", "icon": "heart-pulse", "badge": "Medical Emergency"},
    "Missing Person": {"color": "#A855F7", "icon": "user-search", "badge": "Missing Person"},
    "Other Emergency": {"color": "#1E293B", "icon": "alert-octagon", "badge": "Critical Emergency"}
}

@router.get("/incidents")
def get_map_incidents(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    query = db.query(Incident)
    if category and category.lower() != "all":
        query = query.filter(Incident.category == category)
    if severity and severity.lower() != "all":
        query = query.filter(Incident.severity == severity)
    if status and status.lower() != "all":
        query = query.filter(Incident.status == status)

    incidents = query.all()
    is_authority = current_user and current_user.role == "authority"

    features = []
    for inc in incidents:
        lat = inc.latitude if is_authority else (inc.public_safe_latitude or inc.latitude)
        lng = inc.longitude if is_authority else (inc.public_safe_longitude or inc.longitude)

        if inc.status == "Resolved":
            color = "#10B981"  # GREEN for resolved
            icon = "check-circle"
        elif inc.severity == "Critical":
            color = "#0F172A"  # BLACK/DARK for major/critical
            icon = "alert-octagon"
        else:
            meta = CATEGORY_VISUAL_MAP.get(inc.category, {"color": "#64748B", "icon": "info"})
            color = meta["color"]
            icon = meta["icon"]

        features.append({
            "id": inc.id,
            "reference_id": inc.reference_id,
            "title": inc.title,
            "category": inc.category,
            "severity": inc.severity,
            "status": inc.status,
            "verification_status": inc.verification_status,
            "description": inc.description[:180] + "..." if len(inc.description) > 180 else inc.description,
            "latitude": lat,
            "longitude": lng,
            "address": inc.address,
            "landmark": inc.landmark,
            "people_affected": inc.people_affected,
            "assigned_team": inc.assigned_team if is_authority else None,
            "color": color,
            "icon": icon,
            "created_at": inc.created_at.isoformat(),
            "updated_at": inc.updated_at.isoformat(),
            "evidence_count": len(inc.evidence)
        })

    return features

@router.get("/zones")
def get_map_activity_zones(db: Session = Depends(get_db)):
    """Returns aggregated incident clusters using responsible community terminology."""
    return IncidentService.calculate_activity_zones(db)

@router.get("/resources")
def get_nearby_resources():
    """Demo emergency infrastructure locations for Meerut City & Cantt."""
    return [
        {
            "id": "res_1",
            "name": "Civil Lines Police Station, Meerut",
            "type": "Police Station",
            "latitude": 28.9910,
            "longitude": 77.7150,
            "contact": "0121-2640100",
            "icon": "shield"
        },
        {
            "id": "res_2",
            "name": "LLRM Medical College & Hospital",
            "type": "Emergency Hospital",
            "latitude": 28.9610,
            "longitude": 77.7600,
            "contact": "0121-2760888",
            "icon": "hospital"
        },
        {
            "id": "res_3",
            "name": "Meerut Cantt Fire Station",
            "type": "Fire Station",
            "latitude": 28.9960,
            "longitude": 77.7120,
            "contact": "101",
            "icon": "truck"
        },
        {
            "id": "res_4",
            "name": "Sadar Bazaar Police Post, Meerut",
            "type": "Police Booth",
            "latitude": 28.9870,
            "longitude": 77.7030,
            "contact": "0121-2661100",
            "icon": "shield"
        }
    ]
