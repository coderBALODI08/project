@echo off
echo ==========================================================
echo    SURAKSHA - Smart Citizen Safety & Response Platform   
echo ==========================================================
cd /d "%~dp0backend"

set PYTHONPATH=.
echo [*] Starting SURAKSHA Unified Application Server...
echo [*] Open in your browser: http://localhost:8000
echo [*] API Docs:             http://localhost:8000/docs
echo [*] Citizen Demo:         citizen@suraksha.demo / Citizen@123
echo [*] Authority Demo:       officer@suraksha.demo / Officer@123
echo ----------------------------------------------------------

if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
) else (
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
)
pause
