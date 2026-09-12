from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    role = Column(String(50), default="citizen", nullable=False)  # 'citizen', 'authority', 'admin'
    badge_number = Column(String(100), nullable=True)  # For authority
    department = Column(String(100), nullable=True)    # For authority e.g., 'Traffic Control', 'Fire & Rescue'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    incidents = relationship("Incident", back_populates="reporter", foreign_keys="Incident.reported_by_id")
    assigned_incidents = relationship("Incident", back_populates="assigned_officer", foreign_keys="Incident.assigned_to_id")
    sos_alerts = relationship("SOSAlert", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
