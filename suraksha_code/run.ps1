# SURAKSHA One-Click PowerShell Launcher
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   SURAKSHA - Smart Citizen Safety & Response Platform   " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

$BackendDir = Join-Path $PSScriptRoot "backend"
Set-Location $BackendDir

$VenvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "[!] Virtual environment not found. Setting up with UV..." -ForegroundColor Yellow
    & "$HOME\.local\bin\uv.exe" venv .venv --python 3.11
    & "$HOME\.local\bin\uv.exe" pip install -r requirements.txt --python .venv
}

$env:PYTHONPATH = "."
Write-Host "[*] Starting SURAKSHA Unified Application Server..." -ForegroundColor Green
Write-Host "[*] Frontend available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "[*] API Documentation at:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "[*] Citizen Demo:          citizen@suraksha.demo / Citizen@123" -ForegroundColor White
Write-Host "[*] Authority Demo:        officer@suraksha.demo / Officer@123" -ForegroundColor White
Write-Host "----------------------------------------------------------"

& $VenvPython -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
