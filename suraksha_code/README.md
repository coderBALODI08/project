# SURAKSHA — Smart Citizen Safety & Real-Time Incident Response Platform

> **"Your safety. Your voice. Faster emergency response."**  
> SURAKSHA is a citizen-first interactive safety and incident response platform designed to bridge the communication gap between citizens and law-enforcement/emergency authorities during incidents (fires, road accidents, medical emergencies, suspicious activities, missing persons, and critical hazards).

---

## 🌟 Highlights & Key Capabilities

1. **Human-Centered & Usable under Stress**  
   Designed with calm, trustworthy aesthetics (deep navy `#0B192C`, emergency red `#DC2626`, safe green `#059669`). Minimizes cognitive load with touch-friendly controls, 1-click actions, and reassuring humanized messaging ("Help is closer than you think").

2. **Interactive Safety Map (Leaflet.js + OpenStreetMap)**  
   - Real, genuinely interactive spatial mapping (zoom, pan, geolocation).
   - Category-coded accessible pin markers with symbols and text labels.
   - Responsible "Recent Incident Activity" zones (translucent aggregation circles, avoiding neighborhood stigmatization).
   - Emergency infrastructure layers (Police booths, Hospitals, Fire stations).

3. **5-Step Multi-Stage Reporting Wizard**  
   - **Step 1:** What happened? (Large category selector: Fire, Road Accident, Suspicious Activity, Medical Emergency, Missing Person, Critical Emergency).
   - **Step 2:** Where did it happen? (Interactive map pin picker with draggable marker, "Use My Location" GPS button, Address & Landmark inputs).
   - **Step 3:** Tell us more (Title, Severity: Low/Moderate/High/Critical, Description, People Affected, Reporter contact).
   - **Step 4:** Add evidence (Photo upload with drag-and-drop and live thumbnail preview grid).
   - **Step 5:** Review & Submit (Structured preview -> Generates `SUR-2026-XXXXXX` tracking ID).

4. **Closed-Loop Response Tracking**  
   Eliminates the "black hole" of citizen reporting:
   $$\text{Report Submitted} \longrightarrow \text{Report Received} \longrightarrow \text{Under Verification} \longrightarrow \text{Authority Assigned} \longrightarrow \text{Action Taken} \longrightarrow \text{Resolved}$$
   Every step records timestamps, dispatcher comments, and responding officer identity.

5. **SOS Emergency Experience**  
   - Distinct, glowing red emergency action button accessible across all pages.
   - Quick safety confirmation dialog ("Send emergency alert with your current location?").
   - Instant GPS distress broadcast generating `SOS-2026-XXXXXX`.
   - Visual status progression: Alert Sent $\to$ Received $\to$ Response Initiated.
   - Fast-dial directory for official emergency hotlines (112, 100, 108, 101, 1090).

6. **SURAKSHA Command Center (Police & Dispatcher Portal)**  
   - Live KPI operations counters: Total Today, Active Incidents, Active SOS Alerts, Pending Verification, Critical / High / Moderate / Resolved.
   - Active SOS Alert banner with flashing beacon and unit dispatch controls.
   - Incident Triage Table with multi-criteria filtering (category, status, severity, full-text search).
   - Evidence inspector modal for photographic verification.
   - Tactical Live Map with real-time inspector sidebar and 1-click status transitions (`VERIFIED`, `REJECTED`, `ASSIGN UNIT`, `RESOLVED`).

7. **Privacy-by-Design**  
   - Coordinates rendered on the public citizen map are gently obfuscated by ~100–150m to prevent pinpointing private homes.
   - Exact coordinates and reporter contact are accessible only to authenticated emergency authorities.
   - Secure UUID image handling with MIME and file size validation (5MB max).

---

## 🏗️ Architecture & Tech Stack

```
suraksha/
├── backend/
│   ├── app/
│   │   ├── auth/            # JWT tokens & PBKDF2/Bcrypt password hashing
│   │   ├── models/          # SQLAlchemy Relational Models (User, Incident, Evidence, History, SOS, Notification, Audit)
│   │   ├── schemas/         # Pydantic v2 validation & response schemas
│   │   ├── routers/         # Clean REST endpoints (auth, incidents, sos, map, notifications, dashboard, authority)
│   │   ├── services/        # Business logic (IncidentService, SOSService, NotificationService, SeedService)
│   │   ├── utils/           # Secure file handler & image MIME validator
│   │   ├── config.py        # Pydantic Settings & environment variables
│   │   ├── database.py      # SQLAlchemy engine with PostgreSQL & SQLite fallback
│   │   └── main.py          # FastAPI application & static frontend mount
│   ├── tests/               # Pytest automated test suite (10/10 passing)
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html           # Public landing page
│   ├── login.html           # Citizen login with 1-click demo filler
│   ├── register.html        # Citizen self-registration
│   ├── dashboard.html       # Citizen monitored dashboard & nearby feed
│   ├── map.html             # Interactive community safety map
│   ├── report.html          # 5-step incident reporting wizard
│   ├── reports.html         # Closed-loop tracking timeline & history
│   ├── safety.html          # Citizen safety center & emergency guides
│   ├── profile.html         # Citizen profile, notifications & privacy policy
│   ├── authority/
│   │   ├── login.html       # Official Command Center login
│   │   ├── dashboard.html   # Command Center operational KPIs & SOS monitor
│   │   ├── incidents.html   # Incident triage table & evidence viewer
│   │   └── map.html         # Tactical live GIS map & split inspector
│   ├── css/                 # main.css, components.css, authority.css, responsive.css
│   └── js/                  # api.js, auth.js, app.js, map.js, report.js, reports.js, sos.js, notifications.js, authority.js
├── run.ps1                  # 1-Click PowerShell launcher
├── run.bat                  # 1-Click Windows Command Prompt launcher
├── docker-compose.yml       # Production container orchestration
└── README.md
```

---

## 🚀 Getting Started

### Quick Start (Windows PowerShell)

Run the included launcher script from the `suraksha` directory:
```powershell
.\run.ps1
```

Or execute manually with Python / UV:
```powershell
cd backend
$env:PYTHONPATH = "."
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser to:
- **Application Web UI:** [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI / Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 👥 Pre-Seeded Demo Accounts

The database automatically seeds realistic fictional demo data upon initial launch (situated in central New Delhi / Connaught Place with fire, road accidents, medical distress, missing child, and active SOS alerts). Both login forms feature **1-click "Quick SIH Demo Fill"** buttons for effortless evaluation:

| Role | Email | Password | Access Area |
| :--- | :--- | :--- | :--- |
| **Citizen Demo** | `citizen@suraksha.demo` | `Citizen@123` | Citizen Dashboard, Map, Report Wizard, My Reports |
| **Authority Demo** | `officer@suraksha.demo` | `Officer@123` | Command Center, Incident Triage, Tactical Map |

---

## 🧪 Running Automated Tests

Run the backend test suite covering authentication, RBAC, incident creation, status updating, SOS workflow, and dashboard endpoints:
```powershell
cd backend
$env:PYTHONPATH = "."
.\.venv\Scripts\pytest.exe -v tests/test_api.py
```
*Result: 10 / 10 tests passing.*

---

## 🛡️ Official Emergency Disclaimer
SURAKSHA is a civic technology incident reporting and community awareness coordination platform. In any active, life-threatening situation, citizens are instructed to immediately dial official emergency services directly (**112** for All Emergencies, **100** for Police, **108** for Ambulance, **101** for Fire, and **1090** for Women Helpline).
