import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.config import settings

def save_evidence_file(file: UploadFile, incident_id: int) -> dict:
    # Validate content type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}. Please upload JPG, PNG, or WEBP images."
        )

    # Sanitize and create unique filename
    extension = Path(file.filename).suffix.lower()
    if not extension:
        extension = ".jpg"
    unique_filename = f"evidence_inc_{incident_id}_{uuid.uuid4().hex[:10]}{extension}"
    target_path = settings.UPLOAD_DIR / unique_filename

    # Read and validate file size (max 5MB)
    file_bytes = file.file.read()
    file_size = len(file_bytes)
    if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    # Save to disk
    with open(target_path, "wb") as buffer:
        buffer.write(file_bytes)

    return {
        "file_name": file.filename or unique_filename,
        "file_path": f"/uploads/{unique_filename}",
        "file_type": file.content_type,
        "file_size": file_size
    }
