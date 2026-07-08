from tests.conftest import make_workbook_bytes, valid_row


def test_upload_saves_only_valid_rows(client):
    file_bytes = make_workbook_bytes([
        valid_row(),
        valid_row(**{"Import Volume": -1, "Country of Origin": "Germany"}),
    ])

    response = client.post(
        "/upload",
        files={"file": ("cbam.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_rows"] == 2
    assert payload["valid_rows"] == 1
    assert payload["invalid_rows"] == 1
    assert len(payload["errors"]) >= 2

    records_response = client.get("/records?page=1&page_size=20")
    assert records_response.status_code == 200
    assert records_response.json()["total"] == 1


def test_upload_rejects_non_xlsx_extension(client):
    response = client.post(
        "/upload",
        files={"file": ("cbam.csv", b"not excel", "text/csv")},
    )
    assert response.status_code == 400


def test_upload_rejects_invalid_headers(client):
    file_bytes = make_workbook_bytes([valid_row()], headers=["Wrong Header"])
    response = client.post(
        "/upload",
        files={"file": ("cbam.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["message"] == "Invalid template headers"
