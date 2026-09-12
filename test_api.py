import pytest
from fastapi.testclient import TestClient
from app.main import app

# Use TestClient as a context manager so lifespan (init_db + seed) runs properly
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "SURAKSHA" in data["service"]

def test_frontend_routes_served(client):
    routes = [
        "/",
        "/login.html",
        "/register.html",
        "/dashboard.html",
        "/map.html",
        "/report.html",
        "/reports.html",
        "/safety.html",
        "/profile.html",
        "/authority/login.html",
        "/authority/dashboard.html",
        "/authority/incidents.html",
        "/authority/map.html",
        "/css/main.css",
        "/js/app.js",
        "/js/map.js",
        "/js/sos.js"
    ]
    for r in routes:
        res = client.get(r)
        assert res.status_code == 200, f"Route {r} failed with {res.status_code}"

def test_auth_login_citizen(client):
    response = client.post("/api/auth/login", json={
        "email": "citizen@suraksha.demo",
        "password": "Citizen@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "citizen"

def test_auth_login_authority(client):
    response = client.post("/api/auth/login", json={
        "email": "officer@suraksha.demo",
        "password": "Officer@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "authority"

def test_list_incidents(client):
    response = client.get("/api/incidents")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    first = data[0]
    assert "reference_id" in first
    assert first["reference_id"].startswith("SUR-2026-")

def test_map_endpoints(client):
    inc_res = client.get("/api/map/incidents")
    assert inc_res.status_code == 200
    inc_data = inc_res.json()
    assert len(inc_data) > 0
    assert "color" in inc_data[0]
    assert "icon" in inc_data[0]

    zones_res = client.get("/api/map/zones")
    assert zones_res.status_code == 200
    zones_data = zones_res.json()
    assert isinstance(zones_data, list)

def test_incident_detail_timeline(client):
    list_res = client.get("/api/incidents")
    ref = list_res.json()[0]["reference_id"]

    detail_res = client.get(f"/api/incidents/{ref}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["reference_id"] == ref
    assert "status_history" in detail
    assert len(detail["status_history"]) >= 1

def test_create_and_track_incident(client):
    login_res = client.post("/api/auth/login", json={
        "email": "citizen@suraksha.demo",
        "password": "Citizen@123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_payload = {
        "title": "Pedestrian Stumble & Sprain near Metro Gate",
        "category": "Medical Emergency",
        "severity": "Moderate",
        "description": "Pedestrian slipped on wet tiles near stairs. Needs first aid and ankle support.",
        "latitude": 28.9850,
        "longitude": 77.7070,
        "address": "Begum Bridge Market Crossing, Meerut",
        "landmark": "Near PL Sharma Market",
        "people_affected": 1
    }

    create_res = client.post("/api/incidents", json=create_payload, headers=headers)
    assert create_res.status_code == 201
    created_inc = create_res.json()
    assert created_inc["reference_id"].startswith("SUR-2026-")
    assert created_inc["category"] == "Medical Emergency"

    ref = created_inc["reference_id"]
    track_res = client.get(f"/api/incidents/{ref}")
    assert track_res.status_code == 200
    assert track_res.json()["status"] == "Submitted"

def test_authority_status_update_and_rbac(client):
    citizen_login = client.post("/api/auth/login", json={
        "email": "citizen@suraksha.demo",
        "password": "Citizen@123"
    })
    citizen_token = citizen_login.json()["access_token"]

    list_res = client.get("/api/incidents")
    target_id = list_res.json()[0]["id"]

    forbidden_res = client.put(
        f"/api/incidents/{target_id}/status",
        json={"status": "Action Taken", "comment": "Unauthorized attempt"},
        headers={"Authorization": f"Bearer {citizen_token}"}
    )
    assert forbidden_res.status_code == 403

    officer_login = client.post("/api/auth/login", json={
        "email": "officer@suraksha.demo",
        "password": "Officer@123"
    })
    officer_token = officer_login.json()["access_token"]

    allowed_res = client.put(
        f"/api/incidents/{target_id}/status",
        json={"status": "Action Taken", "verification_status": "Verified", "comment": "Emergency team on site."},
        headers={"Authorization": f"Bearer {officer_token}"}
    )
    assert allowed_res.status_code == 200
    assert allowed_res.json()["status"] == "Action Taken"

def test_sos_workflow(client):
    sos_payload = {
        "latitude": 28.9860,
        "longitude": 77.7040,
        "address": "Near Ghanta Ghar, Sadar Bazaar, Meerut",
        "user_name": "Citizen Test",
        "user_phone": "+91 99999 88888",
        "notes": "Testing SOS trigger event."
    }
    sos_res = client.post("/api/sos", json=sos_payload)
    assert sos_res.status_code == 201
    sos_data = sos_res.json()
    assert sos_data["reference_id"].startswith("SOS-2026-")
    assert sos_data["status"] == "ALERT_SENT"
    assert "112" in sos_data["emergency_services"].values()

def test_dashboard_endpoints(client):
    c_res = client.get("/api/dashboard/citizen")
    assert c_res.status_code == 200
    c_data = c_res.json()
    assert "monitored_status" in c_data
    assert "safety_message" in c_data

    officer_login = client.post("/api/auth/login", json={
        "email": "officer@suraksha.demo",
        "password": "Officer@123"
    })
    token = officer_login.json()["access_token"]

    a_res = client.get("/api/dashboard/authority", headers={"Authorization": f"Bearer {token}"})
    assert a_res.status_code == 200
    a_data = a_res.json()
    assert "total_incidents_today" in a_data
    assert "sos_alerts_active" in a_data
    assert "category_breakdown" in a_data
