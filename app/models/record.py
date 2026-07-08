from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Date, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CBAMRecord(Base):
    """
    Representa un registro importado desde un archivo Excel validado.
    """
    __tablename__ = "cbam_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    upload_batch_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)

    eori_number: Mapped[str] = mapped_column(String(17), nullable=False, index=True)
    declarant_legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    declarant_address: Mapped[str] = mapped_column(Text, nullable=False)
    contact_person: Mapped[str] = mapped_column(String(255), nullable=False)
    competent_authority: Mapped[str] = mapped_column(String(255), nullable=False)
    cbam_account_number: Mapped[str] = mapped_column(String(80), nullable=False)
    data_owner: Mapped[str] = mapped_column(String(255), nullable=False)
    taric_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    cn_code: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    goods_description: Mapped[str] = mapped_column(Text, nullable=False)
    sector_category: Mapped[str] = mapped_column(String(80), nullable=False)
    product_type: Mapped[str] = mapped_column(String(20), nullable=False)
    import_volume: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    date_of_importation: Mapped[date] = mapped_column(Date, nullable=False)
    country_of_origin: Mapped[str] = mapped_column(String(100), nullable=False)
    customs_declaration_ref: Mapped[str | None] = mapped_column(String(120), nullable=True)
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False)
    notes_comments: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
