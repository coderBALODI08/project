from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., SUR-2026-004821
    title = Column(String(255), nullable=False)
    category = Column(String(100), index=True, nullable=False)  # Fire, Road Accident, Suspicious Activity, etc.
    severity = Column(String(50), default="Moderate", index=True, nullable=False)  # Low, Moderate, High, Critical
    status = Column(String(50), default="Submitted", index=True, nullable=False)  # Submitted, Received, Under Verification, Authority Assigned, Action Taken, Resolved, Rejected
    verification_status = Column(String(50), default="Under Review", index=True, nullable=False)  # Unverified, Under Review, Verified, Rejected
    
    description = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(500), nullable=False)
    landmark = Column(String(255), nullable=True)
    people_affected = Column(Integer, default=0, nullable=True)

    # Privacy preservation: Public-safe coordinates (fuzzed/approximate for public citizen view)
    public_safe_latitude = Column(Float, nullable=True)
    public_safe_longitude = Column(Float, nullable=True)

    # Reporter linkage (nullable for guest/anonymous)
    reported_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reporter_name = Column(String(255), nullable=True)
    reporter_contact = Column(String(100), nullable=True)
    is_anonymous = Column(Integer, default=0)

    # Authority assignment
    assigned_to_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_team = Column(String(150), nullable=True)
    internal_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reporter = relationship("User", back_populates="incidents", foreign_keys=[reported_by_id])
    assigned_officer = relationship("User", back_populates="assigned_incidents", foreign_keys=[assigned_to_id])
    evidence = relationship("IncidentEvidence", back_populates="incident", cascade="all, delete-orphan")
    status_history = relationship("IncidentStatusHistory", back_populates="incident", cascade="all, delete-orphan", order_by="IncidentStatusHistory.timestamp.asc()")
