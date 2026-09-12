from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict

class SOSCreate(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = "Current Citizen Location"
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    notes: Optional[str] = None

class SOSUpdate(BaseModel):
    status: str
    dispatched_unit: Optional[str] = None
    notes: Optional[str] = None

class SOSOut(BaseModel):
    id: int
    reference_id: str
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    latitude: float
    longitude: float
    address: Optional[str] = None
    status: str
    dispatched_unit: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    emergency_services: Dict[str, str] = {}

    model_config = ConfigDict(from_attributes=True)
