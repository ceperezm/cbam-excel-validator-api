from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.record import CBAMRecord
from app.schemas.record import PaginatedRecords, RecordRead

router = APIRouter(tags=["records"])


@router.get("/records", response_model=PaginatedRecords)
def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedRecords:
    """
    Consulta la base de datos para obtener los registros guardados previamente.
    Utiliza paginacion para no saturar la respuesta, devolviendo solo la porcion solicitada.
    """
    total = db.scalar(select(func.count()).select_from(CBAMRecord)) or 0
    offset = (page - 1) * page_size
    records = db.scalars(
        select(CBAMRecord)
        .order_by(CBAMRecord.id.asc())
        .offset(offset)
        .limit(page_size)
    ).all()
    return PaginatedRecords(
        page=page,
        page_size=page_size,
        total=total,
        items=[RecordRead.model_validate(record) for record in records],
    )
