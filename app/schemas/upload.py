from pydantic import BaseModel, Field


class RowValidationError(BaseModel):
    row: int = Field(..., examples=[7])
    field: str = Field(..., examples=["Country of Origin"])
    value: str | int | float | None = Field(None, examples=["Germany"])
    message: str = Field(..., examples=["Country of origin must be outside EU/exempt countries"])


class UploadResponse(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    saved_batch_id: str | None = None
    errors: list[RowValidationError]
