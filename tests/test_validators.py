from app.services.validators import validate_record
from tests.conftest import valid_row


def test_valid_record_passes_validation():
    sanitized, errors = validate_record(valid_row())
    assert errors == []
    assert sanitized is not None
    assert sanitized["cn_code"] == "72071114"
    assert sanitized["country_of_origin"] == "China"


def test_invalid_email_and_negative_volume_are_reported():
    sanitized, errors = validate_record(
        valid_row(**{"Contact Person": "John Doe correo-invalido", "Import Volume": -5})
    )
    assert sanitized is None
    assert {error.field for error in errors} >= {"Contact Person", "Import Volume"}


def test_eu_country_of_origin_is_rejected():
    sanitized, errors = validate_record(valid_row(**{"Country of Origin": "Germany"}))
    assert sanitized is None
    assert any(error.field == "Country of Origin" for error in errors)
