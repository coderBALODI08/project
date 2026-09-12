from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class EvidenceOut(BaseModel):
    id: int
    incident_id: int
    file_path: str
    file_name: str
    file_type: str
    file_size: int
    caption: Optional[str] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)

class StatusHistoryOut(BaseModel):
    id: int
    status: str
    comment: Optional[str] = None
    changed_by_name: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class IncidentBase(BaseModel):
    title: str
    category: str  # Fire, Road Accident, Suspicious Activity, Medical Emergency, Missing Person, Other Emergency
    severity: str = "Moderate"  # Low, Moderate, High, Critical
    description: str
    latitude: float
    longitude: float
    address: str
    landmark: Optional[str] = None
    people_affected: Optional[int] = 0
    reporter_name: Optional[str] = None
    reporter_contact: Optional[str] = None
    is_anonymous: Optional[int] = 0

class IncidentCreate(IncidentBase):
    pass

class IncidentPublicSafeOut(BaseModel):
    id: int
    reference_id: str
    title: str
    category: str
    severity: str
    status: str
    latitude: float  # public-safe approximate coordinate
    longitude: float # public-safe approximate coordinate
    address: str
    landmark: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    evidence_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class IncidentOut(IncidentBase):
    id: int
    reference_id: str
    status: str
    verification_status: str
    reported_by_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    assigned_team: Optional[str] = None
    internal_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    evidence: List[EvidenceOut] = []
    status_history: List[StatusHistoryOut] = []

    model_config = ConfigDict(from_attributes=True)

class IncidentUpdateStatus(BaseModel):
    status: str
    comment: Optional[str] = None
    verification_status: Optional[str] = None
    internal_notes: Optional[str] = None

class IncidentAssign(BaseModel):
    assigned_to_id: Optional[int] = None
    assigned_team: Optional[str] = None
    note: Optional[str] = None
