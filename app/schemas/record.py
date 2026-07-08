from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class RecordRead(BaseModel):
    id: int
    upload_batch_id: str
    eori_number: str
    declarant_legal_name: str
    declarant_address: str
    contact_person: str
    competent_authority: str
    cbam_account_number: str
    data_owner: str
    taric_code: str | None
    cn_code: str
    goods_description: str
    sector_category: str
    product_type: str
    import_volume: Decimal
    date_of_importation: date
    country_of_origin: str
    customs_declaration_ref: str | None
    supplier_name: str
    notes_comments: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedRecords(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[RecordRead]
