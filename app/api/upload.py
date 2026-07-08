from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.upload import UploadResponse
from app.services.upload_service import process_upload

router = APIRouter(tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_xlsx(file: UploadFile = File(...), db: Session = Depends(get_db)) -> UploadResponse:
    """
    Lee el archivo cargado y delega la validacion y el guardado al servicio.
    """
    file_bytes = await file.read()
    return process_upload(file_bytes=file_bytes, filename=file.filename, db=db)
