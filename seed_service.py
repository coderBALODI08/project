from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.incident import Incident
from app.models.status_history import IncidentStatusHistory
from app.models.sos import SOSAlert
from app.models.notification import Notification
from app.auth.security import get_password_hash

def seed_database_if_empty(db: Session):
    # Check if users already exist
    existing_user = db.query(User).first()
    if existing_user:
        return

    print("[SURAKSHA] Seeding initial demo users and realistic incidents for Meerut...")

    # 1. Create Demo Users
    citizen_user = User(
        email="citizen@suraksha.demo",
        hashed_password=get_password_hash("Citizen@123"),
        full_name="Aarav Sharma",
        phone="+91 98765 43210",
        role="citizen",
        is_active=True,
        created_at=datetime.utcnow() - timedelta(days=5)
    )
    db.add(citizen_user)

    officer_user = User(
        email="officer@suraksha.demo",
        hashed_password=get_password_hash("Officer@123"),
        full_name="Inspector Rajesh Verma",
        phone="+91 91234 56789",
        role="authority",
        badge_number="UP-MRT-7721",
        department="Meerut Police Central Emergency & Traffic Division",
        is_active=True,
        created_at=datetime.utcnow() - timedelta(days=30)
    )
    db.add(officer_user)

    responder_user = User(
        email="paramedic@suraksha.demo",
        hashed_password=get_password_hash("Responder@123"),
        full_name="Dr. Sneha Patel",
        phone="+91 99887 76655",
        role="authority",
        badge_number="MRT-AMB-108",
        department="Emergency Medical Services (LLRM Meerut)",
        is_active=True,
        created_at=datetime.utcnow() - timedelta(days=20)
    )
    db.add(responder_user)
    db.flush()

    # 2. Seed Realistic Incidents across all required categories for Meerut (Center: ~28.9845, 77.7064)
    sample_incidents = [
        {
            "reference_id": "SUR-2026-004821",
            "title": "Commercial Electrical Transformer Fire",
            "category": "Fire",
            "severity": "High",
            "status": "Authority Assigned",
            "verification_status": "Verified",
            "description": "Thick black smoke and sparks emitting from roadside commercial transformer near PL Sharma Market. Nearby shops evacuated as precaution. Fire tender en-route.",
            "latitude": 28.9896,
            "longitude": 77.7088,
            "address": "Begum Bridge Road, Near PL Sharma Market, Meerut",
            "landmark": "Opposite Begum Bridge Crossing",
            "people_affected": 12,
            "reported_by_id": citizen_user.id,
            "reporter_name": "Aarav Sharma",
            "reporter_contact": "+91 98765 43210",
            "assigned_to_id": officer_user.id,
            "assigned_team": "Cantt Fire Station Tender 02 & Traffic Unit",
            "internal_notes": "Power discom sub-station notified. Traffic on Begum Bridge diverted toward Abu Lane.",
            "hours_ago": 2
        },
        {
            "reference_id": "SUR-2026-003914",
            "title": "Truck and Delivery Van Collision",
            "category": "Road Accident",
            "severity": "Moderate",
            "status": "Action Taken",
            "verification_status": "Verified",
            "description": "Rear-end collision between a medium freight truck and mini-van on Delhi Road. Mini-van driver sustained minor cuts. Traffic backup extending 300 meters.",
            "latitude": 28.9480,
            "longitude": 77.6740,
            "address": "Delhi Road, Near Partapur Flyover, Meerut",
            "landmark": "Near Rithani Crossing",
            "people_affected": 2,
            "reported_by_id": None,
            "reporter_name": "Rohan Mehra",
            "reporter_contact": "+91 98112 34567",
            "assigned_to_id": officer_user.id,
            "assigned_team": "Partapur Highway Patrol Unit 3",
            "internal_notes": "Vehicles towed to service lane. First aid administered on site. Traffic cleared.",
            "hours_ago": 4
        },
        {
            "reference_id": "SUR-2026-005102",
            "title": "Unattended Metallic Luggage Bag",
            "category": "Suspicious Activity",
            "severity": "High",
            "status": "Under Verification",
            "verification_status": "Under Review",
            "description": "Dark grey hard-shell briefcase left unattended on pedestrian walkway for over 40 minutes near shopping arcade entrance. Market association alerted.",
            "latitude": 28.9880,
            "longitude": 77.7060,
            "address": "Main Abu Lane Market, Meerut Cantt",
            "landmark": "Near Bombay Bazaar Entrance",
            "people_affected": 0,
            "reported_by_id": citizen_user.id,
            "reporter_name": "Aarav Sharma",
            "reporter_contact": "+91 98765 43210",
            "assigned_to_id": officer_user.id,
            "assigned_team": "Sadar Police Beat Unit & Bomb Detection Squad",
            "internal_notes": "15-meter security cordon placed. CCTV camera footage from nearby garment store being scanned.",
            "hours_ago": 1
        },
        {
            "reference_id": "SUR-2026-002844",
            "title": "Elderly Citizen Heatstroke / Severe Collapse",
            "category": "Medical Emergency",
            "severity": "Critical",
            "status": "Authority Assigned",
            "verification_status": "Verified",
            "description": "Elderly pedestrian collapsed on the sidewalk due to severe dehydration/heat exhaustion. Pulse weak and breathing shallow. Local shopkeeper provided shade and cold water.",
            "latitude": 28.9610,
            "longitude": 77.7600,
            "address": "Garh Road, Near LLRM Medical College Gate, Meerut",
            "landmark": "Outside Trauma Center Walkway",
            "people_affected": 1,
            "reported_by_id": None,
            "reporter_name": "Priya Sen",
            "reporter_contact": "+91 97113 45678",
            "assigned_to_id": responder_user.id,
            "assigned_team": "LLRM Emergency Ambulance 05",
            "internal_notes": "Ambulance arrived on scene. Patient stabilized with IV saline and admitted to emergency ward.",
            "hours_ago": 3
        },
        {
            "reference_id": "SUR-2026-001920",
            "title": "Missing 8-Year-Old Boy in Red Polo Shirt",
            "category": "Missing Person",
            "severity": "Critical",
            "status": "Authority Assigned",
            "verification_status": "Verified",
            "description": "Child separated from mother during peak evening market crowd. Name: Aarush, wearing bright red polo t-shirt, beige cargo shorts, black sandals. Speaks Hindi.",
            "latitude": 28.9660,
            "longitude": 77.7340,
            "address": "Central Market Block B, Shastri Nagar, Meerut",
            "landmark": "Near PVS Mall Road Crossing",
            "people_affected": 1,
            "reported_by_id": None,
            "reporter_name": "Sunita Verma (Mother)",
            "reporter_contact": "+91 98991 23456",
            "assigned_to_id": officer_user.id,
            "assigned_team": "Nauchandi Beat Patrol & Market Security",
            "internal_notes": "Public announcement broadcasted over Shastri Nagar community speakers. Auto stands and bus stops alerted.",
            "hours_ago": 0.5
        },
        {
            "reference_id": "SUR-2026-000841",
            "title": "Broken Tree Branch & Snapped Telecom Cable",
            "category": "Road Accident",
            "severity": "Low",
            "status": "Resolved",
            "verification_status": "Verified",
            "description": "Large eucalyptus branch snapped during morning gusts, dangling low over two-wheeler lane. Potential hazard for cyclists.",
            "latitude": 28.9800,
            "longitude": 77.7350,
            "address": "University Road, Near Saket Crossing, Meerut",
            "landmark": "Near CCS University Main Gate",
            "people_affected": 0,
            "reported_by_id": citizen_user.id,
            "reporter_name": "Aarav Sharma",
            "reporter_contact": "+91 98765 43210",
            "assigned_to_id": officer_user.id,
            "assigned_team": "Meerut Nagar Nigam Quick Response Team",
            "internal_notes": "Branch cleared and debris removed from road shoulder. Lane restored for normal transit.",
            "hours_ago": 24
        },
        {
            "reference_id": "SUR-2026-006319",
            "title": "Commercial Gas Cylinder Valve Leakage",
            "category": "Other Emergency",
            "severity": "Critical",
            "status": "Action Taken",
            "verification_status": "Verified",
            "description": "Hissing commercial LPG cylinder leaking in open loading bay. Strong odor throughout commercial complex. Evacuation initiated.",
            "latitude": 28.9560,
            "longitude": 77.7180,
            "address": "Hapur Road, Transport Nagar Sector 1, Meerut",
            "landmark": "Near Old Bus Stand Commercial Complex",
            "people_affected": 35,
            "reported_by_id": None,
            "reporter_name": "Municipal Officer Tiwari",
            "reporter_contact": "+91 98100 11223",
            "assigned_to_id": officer_user.id,
            "assigned_team": "Civil Lines Fire Station Unit 1 & Gas Techs",
            "internal_notes": "Safety valve clamped. Cylinder submerged in water safety tank. Site declared hazard-free.",
            "hours_ago": 1.5
        }
    ]

    for inc_data in sample_incidents:
        created_time = datetime.utcnow() - timedelta(hours=inc_data["hours_ago"])
        inc = Incident(
            reference_id=inc_data["reference_id"],
            title=inc_data["title"],
            category=inc_data["category"],
            severity=inc_data["severity"],
            status=inc_data["status"],
            verification_status=inc_data["verification_status"],
            description=inc_data["description"],
            latitude=inc_data["latitude"],
            longitude=inc_data["longitude"],
            public_safe_latitude=round(inc_data["latitude"] + 0.0008, 6),
            public_safe_longitude=round(inc_data["longitude"] - 0.0006, 6),
            address=inc_data["address"],
            landmark=inc_data["landmark"],
            people_affected=inc_data["people_affected"],
            reported_by_id=inc_data["reported_by_id"],
            reporter_name=inc_data["reporter_name"],
            reporter_contact=inc_data["reporter_contact"],
            assigned_to_id=inc_data["assigned_to_id"],
            assigned_team=inc_data["assigned_team"],
            internal_notes=inc_data["internal_notes"],
            created_at=created_time,
            updated_at=datetime.utcnow()
        )
        db.add(inc)
        db.flush()

        # Seed realistic closed-loop timeline history
        h1 = IncidentStatusHistory(
            incident_id=inc.id,
            status="Report Submitted",
            comment="Report received and registered in SURAKSHA system.",
            changed_by_name="System",
            timestamp=created_time
        )
        db.add(h1)

        if inc_data["status"] != "Submitted":
            h2 = IncidentStatusHistory(
                incident_id=inc.id,
                status="Under Verification",
                comment="Assigned to central triage desk for initial credibility verification.",
                changed_by_id=officer_user.id,
                changed_by_name=officer_user.full_name,
                timestamp=created_time + timedelta(minutes=6)
            )
            db.add(h2)

        if inc_data["status"] in ["Authority Assigned", "Action Taken", "Resolved"]:
            h3 = IncidentStatusHistory(
                incident_id=inc.id,
                status="Authority Assigned",
                comment=f"Dispatched team {inc_data['assigned_team']}.",
                changed_by_id=officer_user.id,
                changed_by_name=officer_user.full_name,
                timestamp=created_time + timedelta(minutes=14)
            )
            db.add(h3)

        if inc_data["status"] in ["Action Taken", "Resolved"]:
            h4 = IncidentStatusHistory(
                incident_id=inc.id,
                status="Action Taken",
                comment=inc_data["internal_notes"] or "Ground response initiated.",
                changed_by_id=officer_user.id,
                changed_by_name=officer_user.full_name,
                timestamp=created_time + timedelta(minutes=28)
            )
            db.add(h4)

        if inc_data["status"] == "Resolved":
            h5 = IncidentStatusHistory(
                incident_id=inc.id,
                status="Resolved",
                comment="Site secured and verified. Closed by commanding authority.",
                changed_by_id=officer_user.id,
                changed_by_name=officer_user.full_name,
                timestamp=created_time + timedelta(hours=2)
            )
            db.add(h5)

    # 3. Seed active SOS Alert in Meerut
    sample_sos = SOSAlert(
        reference_id="SOS-2026-904122",
        user_id=citizen_user.id,
        user_name=citizen_user.full_name,
        user_phone=citizen_user.phone,
        latitude=28.9860,
        longitude=77.7040,
        address="Near Ghanta Ghar (Clock Tower), Sadar Bazaar, Meerut",
        status="RESPONSE_INITIATED",
        dispatched_unit="PCR Van Cheetah-04 (Sadar Police)",
        notes="Citizen reported feeling unsafe due to persistent harassment near market arcade. PCR van dispatched.",
        created_at=datetime.utcnow() - timedelta(minutes=18),
        updated_at=datetime.utcnow() - timedelta(minutes=5)
    )
    db.add(sample_sos)

    # 4. Seed initial notifications
    sample_notifs = [
        Notification(
            user_id=citizen_user.id,
            target_role="citizen",
            title="Report Status: Authority Assigned",
            message="Your report SUR-2026-004821 (Commercial Electrical Transformer Fire) has been assigned to Cantt Fire Station Tender 02.",
            type="incident_update",
            incident_reference_id="SUR-2026-004821",
            is_read=False,
            created_at=datetime.utcnow() - timedelta(hours=1)
        ),
        Notification(
            user_id=citizen_user.id,
            target_role="citizen",
            title="Incident Resolved",
            message="Your report SUR-2026-000841 (Broken Tree Branch & Snapped Telecom Cable) has been marked as Resolved.",
            type="incident_update",
            incident_reference_id="SUR-2026-000841",
            is_read=True,
            created_at=datetime.utcnow() - timedelta(hours=22)
        ),
        Notification(
            target_role="authority",
            title="ACTIVE SOS ALERT: Sadar Bazaar, Meerut",
            message="SOS-2026-904122 triggered near Ghanta Ghar by Aarav Sharma. PCR Van Cheetah-04 responding.",
            type="sos_alert",
            incident_reference_id="SOS-2026-904122",
            is_read=False,
            created_at=datetime.utcnow() - timedelta(minutes=18)
        )
    ]
    for n in sample_notifs:
        db.add(n)

    db.commit()
    print("[SURAKSHA] Database seeded successfully with Meerut incidents and accounts!")
