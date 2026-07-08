"""crear la tabla cbam_records

ID de revision: 0001_create_cbam_records
Revisiones:
Fecha de creacion: 2026-07-07
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_create_cbam_records"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cbam_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("upload_batch_id", sa.String(length=36), nullable=False),
        sa.Column("eori_number", sa.String(length=17), nullable=False),
        sa.Column("declarant_legal_name", sa.String(length=255), nullable=False),
        sa.Column("declarant_address", sa.Text(), nullable=False),
        sa.Column("contact_person", sa.String(length=255), nullable=False),
        sa.Column("competent_authority", sa.String(length=255), nullable=False),
        sa.Column("cbam_account_number", sa.String(length=80), nullable=False),
        sa.Column("data_owner", sa.String(length=255), nullable=False),
        sa.Column("taric_code", sa.String(length=10), nullable=True),
        sa.Column("cn_code", sa.String(length=8), nullable=False),
        sa.Column("goods_description", sa.Text(), nullable=False),
        sa.Column("sector_category", sa.String(length=80), nullable=False),
        sa.Column("product_type", sa.String(length=20), nullable=False),
        sa.Column("import_volume", sa.Numeric(18, 3), nullable=False),
        sa.Column("date_of_importation", sa.Date(), nullable=False),
        sa.Column("country_of_origin", sa.String(length=100), nullable=False),
        sa.Column("customs_declaration_ref", sa.String(length=120), nullable=True),
        sa.Column("supplier_name", sa.String(length=255), nullable=False),
        sa.Column("notes_comments", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_cbam_records_upload_batch_id", "cbam_records", ["upload_batch_id"])
    op.create_index("ix_cbam_records_eori_number", "cbam_records", ["eori_number"])
    op.create_index("ix_cbam_records_cn_code", "cbam_records", ["cn_code"])


def downgrade() -> None:
    op.drop_index("ix_cbam_records_cn_code", table_name="cbam_records")
    op.drop_index("ix_cbam_records_eori_number", table_name="cbam_records")
    op.drop_index("ix_cbam_records_upload_batch_id", table_name="cbam_records")
    op.drop_table("cbam_records")
