import random
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.models.incident import Incident
from app.models.status_history import IncidentStatusHistory
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.incident import IncidentCreate, IncidentUpdateStatus, IncidentAssign
from app.services.notification_service import NotificationService

class IncidentService:
    @staticmethod
    def generate_reference_id(db: Session) -> str:
        while True:
            rand_num = random.randint(100000, 999999)
            ref_id = f"SUR-2026-{rand_num}"
            existing = db.query(Incident).filter(Incident.reference_id == ref_id).first()
            if not existing:
                return ref_id

    @staticmethod
    def create_incident(
        db: Session,
        incident_data: IncidentCreate,
        user: Optional[User] = None,
        ip_address: Optional[str] = None
    ) -> Incident:
        ref_id = IncidentService.generate_reference_id(db)

        # Public privacy preservation: add a gentle, slight offset (+- 0.001 - 0.0015 deg ~ 100-150m)
        # for public community map views to prevent exact house/residence pinpointing
        jitter_lat = (random.random() - 0.5) * 0.002
        jitter_lng = (random.random() - 0.5) * 0.002
        public_lat = round(incident_data.latitude + jitter_lat, 6)
        public_lng = round(incident_data.longitude + jitter_lng, 6)

        incident = Incident(
            reference_id=ref_id,
            title=incident_data.title,
            category=incident_data.category,
            severity=incident_data.severity or "Moderate",
            status="Submitted",
            verification_status="Under Review",
            description=incident_data.description,
            latitude=incident_data.latitude,
            longitude=incident_data.longitude,
            public_safe_latitude=public_lat,
            public_safe_longitude=public_lng,
            address=incident_data.address,
            landmark=incident_data.landmark,
            people_affected=incident_data.people_affected or 0,
            reported_by_id=user.id if user else None,
            reporter_name=incident_data.reporter_name or (user.full_name if user else "Anonymous Citizen"),
            reporter_contact=incident_data.reporter_contact or (user.phone if user else None),
            is_anonymous=incident_data.is_anonymous or 0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(incident)
        db.flush()

        # Initial closed-loop history entry
        initial_history = IncidentStatusHistory(
            incident_id=incident.id,
            status="Report Submitted",
            comment="Your report has been received and logged into the emergency dispatch queue.",
            changed_by_id=user.id if user else None,
            changed_by_name="System",
            timestamp=datetime.utcnow()
        )
        db.add(initial_history)

        # Audit log
        audit = AuditLog(
            user_id=user.id if user else None,
            user_email=user.email if user else "anonymous",
            action="CREATE_INCIDENT",
            target_type="incident",
            target_id=ref_id,
            details=f"Reported {incident.category} incident at {incident.address}",
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        db.refresh(incident)

        # Notify authorities
        NotificationService.create_notification(
            db=db,
            title=f"New Incident: {incident.category}",
            message=f"A new {incident.severity.lower()} severity incident was reported at {incident.address}. Reference: {ref_id}",
            target_role="authority",
            notification_type="incident_update",
            incident_ref=ref_id
        )

        # Notify citizen if logged in
        if user:
            NotificationService.create_notification(
                db=db,
                title="Report Submitted Successfully",
                message=f"Your incident report for '{incident.title}' has been received. Reference ID: {ref_id}.",
                target_role="citizen",
                user_id=user.id,
                notification_type="incident_update",
                incident_ref=ref_id
            )

        return incident

    @staticmethod
    def update_status(
        db: Session,
        incident_id: int,
        update_data: IncidentUpdateStatus,
        authority_user: User,
        ip_address: Optional[str] = None
    ) -> Incident:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return None

        old_status = incident.status
        incident.status = update_data.status
        if update_data.verification_status:
            incident.verification_status = update_data.verification_status
        if update_data.internal_notes:
            incident.internal_notes = update_data.internal_notes
        incident.updated_at = datetime.utcnow()

        # Closed-loop tracking entry
        comment = update_data.comment or f"Status transitioned from {old_status} to {update_data.status}."
        history_entry = IncidentStatusHistory(
            incident_id=incident.id,
            status=update_data.status,
            comment=comment,
            changed_by_id=authority_user.id,
            changed_by_name=authority_user.full_name,
            timestamp=datetime.utcnow()
        )
        db.add(history_entry)

        # Audit
        audit = AuditLog(
            user_id=authority_user.id,
            user_email=authority_user.email,
            action="UPDATE_STATUS",
            target_type="incident",
            target_id=incident.reference_id,
            details=f"Changed status to {update_data.status}. Note: {comment}",
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        db.refresh(incident)

        # Notify reporter if associated
        if incident.reported_by_id:
            NotificationService.create_notification(
                db=db,
                title=f"Report Update: {incident.reference_id}",
                message=f"Status changed to '{incident.status}'. Note: {comment}",
                target_role="citizen",
                user_id=incident.reported_by_id,
                notification_type="incident_update",
                incident_ref=incident.reference_id
            )

        return incident

    @staticmethod
    def assign_incident(
        db: Session,
        incident_id: int,
        assign_data: IncidentAssign,
        authority_user: User,
        ip_address: Optional[str] = None
    ) -> Incident:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return None

        incident.assigned_to_id = assign_data.assigned_to_id
        if assign_data.assigned_team:
            incident.assigned_team = assign_data.assigned_team
        incident.status = "Authority Assigned"
        incident.updated_at = datetime.utcnow()

        assigned_to_name = assign_data.assigned_team or "Emergency Response Team"
        if assign_data.assigned_to_id:
            officer = db.query(User).filter(User.id == assign_data.assigned_to_id).first()
            if officer:
                assigned_to_name = f"{officer.full_name} ({officer.department or 'Patrol'})"

        comment = assign_data.note or f"Assigned to {assigned_to_name} for on-ground response and verification."
        history_entry = IncidentStatusHistory(
            incident_id=incident.id,
            status="Authority Assigned",
            comment=comment,
            changed_by_id=authority_user.id,
            changed_by_name=authority_user.full_name,
            timestamp=datetime.utcnow()
        )
        db.add(history_entry)

        # Audit
        audit = AuditLog(
            user_id=authority_user.id,
            user_email=authority_user.email,
            action="ASSIGN_INCIDENT",
            target_type="incident",
            target_id=incident.reference_id,
            details=f"Assigned to {assigned_to_name}",
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        db.refresh(incident)

        if incident.reported_by_id:
            NotificationService.create_notification(
                db=db,
                title=f"Officer Assigned: {incident.reference_id}",
                message=f"Your report has been assigned to {assigned_to_name}. Action is currently underway.",
                target_role="citizen",
                user_id=incident.reported_by_id,
                notification_type="incident_update",
                incident_ref=incident.reference_id
            )

        return incident

    @staticmethod
    def get_incidents(
        db: Session,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        verification_status: Optional[str] = None,
        search: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Incident]:
        query = db.query(Incident)

        if user_id:
            query = query.filter(Incident.reported_by_id == user_id)
        if category and category.lower() != "all":
            query = query.filter(Incident.category == category)
        if severity and severity.lower() != "all":
            query = query.filter(Incident.severity == severity)
        if status and status.lower() != "all":
            query = query.filter(Incident.status == status)
        if verification_status and verification_status.lower() != "all":
            query = query.filter(Incident.verification_status == verification_status)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Incident.reference_id.ilike(search_pattern),
                    Incident.title.ilike(search_pattern),
                    Incident.description.ilike(search_pattern),
                    Incident.address.ilike(search_pattern),
                    Incident.category.ilike(search_pattern)
                )
            )

        return query.order_by(desc(Incident.created_at)).limit(limit).all()

    @staticmethod
    def calculate_activity_zones(db: Session) -> List[Dict[str, Any]]:
        """
        Groups active incidents within proximity to produce respectful
        'Recent incident activity' zones rather than stigmatizing labels.
        """
        active_incidents = db.query(Incident).filter(Incident.status != "Resolved").all()
        zones = []
        visited = set()

        for inc in active_incidents:
            if inc.id in visited:
                continue
            
            cluster = [inc]
            visited.add(inc.id)
            
            for other in active_incidents:
                if other.id not in visited:
                    # Rough distance calculation in degrees (~1km is ~0.01 deg)
                    dist = ((inc.latitude - other.latitude)**2 + (inc.longitude - other.longitude)**2)**0.5
                    if dist < 0.015:  # within ~1.5km
                        cluster.append(other)
                        visited.add(other.id)

            if len(cluster) >= 2:
                avg_lat = sum(c.latitude for c in cluster) / len(cluster)
                avg_lng = sum(c.longitude for c in cluster) / len(cluster)
                zones.append({
                    "id": f"zone_{inc.id}",
                    "latitude": round(avg_lat, 6),
                    "longitude": round(avg_lng, 6),
                    "radius_meters": 650 + (len(cluster) * 150),
                    "label": "Recent Incident Activity",
                    "description": f"{len(cluster)} active reports in this vicinity. Exercise awareness.",
                    "incident_count": len(cluster),
                    "level": "Elevated Activity" if len(cluster) > 3 else "Moderate Activity"
                })

        return zones
