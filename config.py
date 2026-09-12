import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "SURAKSHA - Smart Citizen Safety & Real-Time Incident Response Platform"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "suraksha-super-secret-production-quality-key-2026-sih")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database: SQLite local fallback by default, or PostgreSQL if DATABASE_URL provided
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'suraksha.db'}")
    
    # Uploads directory for evidence
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    
    # Emergency numbers configuration
    EMERGENCY_SERVICES: dict[str, str] = {
        "National Emergency (All-in-One)": "112",
        "Police Control Room": "100",
        "Ambulance / Medical Emergency": "108",
        "Fire Rescue Service": "101",
        "Women Safety Helpline": "1090",
        "Childline": "1098"
    }

    DEMO_MODE: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
