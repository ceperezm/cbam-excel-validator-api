from __future__ import annotations

from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.record import CBAMRecord
from app.schemas.upload import RowValidationError, UploadResponse
from app.services.excel_reader import ensure_xlsx_filename, read_data_rows
from app.services.validators import FieldError, validate_record


def build_public_error(row_number: int, error: FieldError) -> RowValidationError:
    value = error.value
    if value is not None and not isinstance(value, (str, int, float)):
        value = str(value)
    return RowValidationError(
        row=row_number,
        field=error.field,
        value=value,
        message=error.message,
    )


def process_upload(file_bytes: bytes, filename: str | None, db: Session) -> UploadResponse:
    """
    Procesa el archivo Excel, valida cada fila y persiste solo los registros validos.
    Devuelve un resumen con los errores de validacion detectados.
    """
    ensure_xlsx_filename(filename)
    rows = read_data_rows(file_bytes)

    batch_id = str(uuid4())
    valid_records: list[CBAMRecord] = []
    public_errors: list[RowValidationError] = []
    invalid_row_numbers: set[int] = set()

    # Valida cada fila y conserva solo las que pasan todas las reglas.
    for row_number, raw_record in rows:
        sanitized, errors = validate_record(raw_record)
        if errors:
            invalid_row_numbers.add(row_number)
            public_errors.extend(build_public_error(row_number, error) for error in errors)
            continue
        assert sanitized is not None
        valid_records.append(CBAMRecord(upload_batch_id=batch_id, **sanitized))

    # Guarda el lote valido en una sola transaccion.
    if valid_records:
        db.add_all(valid_records)
        db.commit()

    return UploadResponse(
        total_rows=len(rows),
        valid_rows=len(valid_records),
        invalid_rows=len(invalid_row_numbers),
        saved_batch_id=batch_id if valid_records else None,
        errors=public_errors,
    )
