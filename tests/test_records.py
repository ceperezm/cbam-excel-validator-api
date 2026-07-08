from tests.conftest import make_workbook_bytes, valid_row


def test_records_endpoint_is_paginated(client):
    file_bytes = make_workbook_bytes([
        valid_row(**{"EORI Number": "DE123456789000001"}),
        valid_row(**{"EORI Number": "DE123456789000002"}),
        valid_row(**{"EORI Number": "DE123456789000003"}),
    ])
    upload = client.post(
        "/upload",
        files={"file": ("cbam.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert upload.status_code == 200

    response = client.get("/records?page=2&page_size=2")
    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 2
    assert payload["page_size"] == 2
    assert payload["total"] == 3
    assert len(payload["items"]) == 1
