from io import BytesIO
import os
from typing import Any

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.services.validators import EXPECTED_HEADERS


@pytest.fixture()
def db_session():
    candidate_urls = [os.getenv("TEST_DATABASE_URL")] if os.getenv("TEST_DATABASE_URL") else [
        "postgresql+psycopg2://cbam:cbam@db:5432/cbam_test",
        "postgresql+psycopg2://cbam:cbam@localhost:5432/cbam_test",
    ]

    database_url = None
    for candidate in candidate_urls:
        if not candidate:
            continue
        db_name = candidate.rsplit("/", 1)[1].split("?", 1)[0]
        admin_url = candidate.rsplit("/", 1)[0] + "/postgres"
        try:
            admin_engine = create_engine(admin_url, future=True, isolation_level="AUTOCOMMIT")
            with admin_engine.connect() as connection:
                exists = connection.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": db_name},
                ).scalar_one_or_none()
                if not exists:
                    connection.execute(text(f'CREATE DATABASE "{db_name}"'))
            admin_engine.dispose()
            database_url = candidate
            break
        except OperationalError:
            continue

    if database_url is None:
        raise RuntimeError("No PostgreSQL instance was reachable for tests. Set TEST_DATABASE_URL explicitly.")

    engine = create_engine(database_url, future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    try:
        with TestingSessionLocal() as session:
            yield session
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def valid_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "EORI Number": "DE123456789012345",
        "Declarant Legal Name": "ArcelorMittal SA",
        "Declarant Address": "24-26 Boulevard d'Avranches, L-1160 Luxembourg",
        "Contact Person": "John Doe, john.doe@company.com",
        "Competent Authority": "DEHSt",
        "CBAM Account Number": "CBAM-DE-2026-00142",
        "Data Owner": "Sam Smith, sam.smith@company.com",
        "TARIC Code": "7207111400",
        "CN Code": "72071114",
        "Goods Description": "Semi-finished iron or non-alloy steel",
        "Sector Category": "Iron and Steel",
        "Product Type": "Complex",
        "Import Volume": 1250.5,
        "Date of importation": "05.05.2026",
        "Country of Origin": "China",
        "Customs Declaration Ref": "DE/2026/MRN-ABC-123456",
        "Supplier Name": "Supplier Ch1",
        "Notes / Comments": "MRV plan is under preparation",
    }
    row.update(overrides)
    return row


def make_workbook_bytes(rows: list[dict[str, Any]], headers: list[str] | None = None) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Template"
    selected_headers = headers or EXPECTED_HEADERS
    ws.append(selected_headers)
    for row in rows:
        ws.append([row.get(header) for header in selected_headers])
    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()
