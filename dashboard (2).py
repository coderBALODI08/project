from typing import Dict, List, Any
from pydantic import BaseModel
from app.schemas.incident import IncidentPublicSafeOut, IncidentOut
from app.schemas.sos import SOSOut

class CitizenDashboardStats(BaseModel):
    monitored_status: str
    safety_message: str
    nearby_incidents_count: int
    active_incidents_nearby: List[IncidentPublicSafeOut]
    my_reports_count: int
    emergency_services: Dict[str, str]

class AuthorityDashboardStats(BaseModel):
    total_incidents_today: int
    active_incidents: int
    sos_alerts_active: int
    pending_verification: int
    critical_incidents: int
    high_incidents: int
    moderate_incidents: int
    resolved_incidents: int
    category_breakdown: Dict[str, int]
    recent_sos_alerts: List[SOSOut]
    recent_incidents: List[IncidentOut]
