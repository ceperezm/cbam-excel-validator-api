from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import pycountry
from pydantic import EmailStr, TypeAdapter, ValidationError

from app.reference_data.cbam_codes import (
    VALID_SECTOR_CATEGORIES,
    infer_sector_from_cn_code,
    is_cbam_annex_i_code,
)
from app.reference_data.competent_authorities import VALID_COMPETENT_AUTHORITIES
from app.reference_data.countries import EXCLUDED_ORIGIN_ALPHA2

EXPECTED_HEADERS = [
    "EORI Number",
    "Declarant Legal Name",
    "Declarant Address",
    "Contact Person",
    "Competent Authority",
    "CBAM Account Number",
    "Data Owner",
    "TARIC Code",
    "CN Code",
    "Goods Description",
    "Sector Category",
    "Product Type",
    "Import Volume",
    "Date of importation",
    "Country of Origin",
    "Customs Declaration Ref",
    "Supplier Name",
    "Notes / Comments",
]

MANDATORY_FIELDS = {
    "EORI Number",
    "Declarant Legal Name",
    "Declarant Address",
    "Contact Person",
    "Competent Authority",
    "CBAM Account Number",
    "Data Owner",
    "CN Code",
    "Goods Description",
    "Sector Category",
    "Product Type",
    "Import Volume",
    "Date of importation",
    "Country of Origin",
    "Supplier Name",
}

EMAIL_ADAPTER = TypeAdapter(EmailStr)
EMAIL_REGEX = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_REGEX = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")
EORI_REGEX = re.compile(r"^[A-Z]{2}[A-Z0-9]{1,15}$")
DIGITS_REGEX = re.compile(r"^\d+$")


@dataclass(frozen=True)
class FieldError:
    field: str
    value: Any
    message: str


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def as_clean_string(value: Any) -> str | None:
    if is_blank(value):
        return None
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def add_error(errors: list[FieldError], field: str, value: Any, message: str) -> None:
    errors.append(FieldError(field=field, value=value, message=message))


def require_text(raw: dict[str, Any], field: str, errors: list[FieldError]) -> str | None:
    value = as_clean_string(raw.get(field))
    if field in MANDATORY_FIELDS and value is None:
        add_error(errors, field, raw.get(field), "This field is required")
        return None
    return value


def validate_eori(raw: dict[str, Any], errors: list[FieldError]) -> str | None:
    field = "EORI Number"
    value = require_text(raw, field, errors)
    if value is None:
        return None
    value = value.upper()
    if len(value) > 17:
        add_error(errors, field, raw.get(field), "EORI Number must have at most 17 characters")
    if not EORI_REGEX.match(value):
        add_error(errors, field, raw.get(field), "Expected format: 2-letter country code + up to 15 alphanumeric characters")
    return value


def validate_non_empty_text(raw: dict[str, Any], field: str, errors: list[FieldError]) -> str | None:
    return require_text(raw, field, errors)


def extract_valid_email(value: str) -> str | None:
    match = EMAIL_REGEX.search(value)
    if not match:
        return None
    email = match.group(0)
    try:
        return str(EMAIL_ADAPTER.validate_python(email))
    except ValidationError:
        return None


def validate_contact_text(raw: dict[str, Any], field: str, errors: list[FieldError]) -> str | None:
    value = require_text(raw, field, errors)
    if value is None:
        return None

    email = extract_valid_email(value)
    phone = PHONE_REGEX.search(value)
    # Regla simple: debe haber un nombre antes del correo o telefono de contacto.
    name_part = value
    if email:
        name_part = value.split(email, 1)[0]
    elif phone:
        name_part = value.split(phone.group(0), 1)[0]

    if not email and not phone:
        add_error(errors, field, raw.get(field), "Must include at least one valid contact method: email or phone")
    if len(name_part.replace(",", " ").strip()) < 3:
        add_error(errors, field, raw.get(field), "Must include the contact person's name")
    return value


def validate_competent_authority(raw: dict[str, Any], errors: list[FieldError]) -> str | None:
    field = "Competent Authority"
    value = require_text(raw, field, errors)
    if value is None:
        return None
    if value not in VALID_COMPETENT_AUTHORITIES:
        add_error(errors, field, raw.get(field), "Must match a valid EU Member State competent authority")
    return value


def validate_digits(raw: dict[str, Any], field: str, length: int, required: bool, errors: list[FieldError]) -> str | None:
    value = as_clean_string(raw.get(field))
    if value is None:
        if required:
            add_error(errors, field, raw.get(field), "This field is required")
        return None
    if not DIGITS_REGEX.match(value):
        add_error(errors, field, raw.get(field), f"Must contain only digits")
    if len(value) != length:
        add_error(errors, field, raw.get(field), f"Must have exactly {length} digits")
    return value


def validate_taric_code(raw: dict[str, Any], errors: list[FieldError]) -> str | None:
    return validate_digits(raw, "TARIC Code", 10, required=False, errors=errors)


def validate_cn_code(raw: dict[str, Any], errors: list[FieldError]) -> str | None:
    field = "CN Code"
    value = validate_digits(raw, field, 8, required=True, errors=errors)
    if value and len(value) == 8 and value.isdigit() and not is_cbam_annex_i_code(value):
        add_error(errors, field, raw.get(field), "CN Code is not included in the configured CBAM Annex I reference list")
    return value


def validate_sector_category(raw: dict[str, Any], cn_code: str | None, errors: list[FieldError]) -> str | None:
    field = "Sector Category"
    value = require_text(raw, field, errors)
    if value is None:
        return None
    if value not in VALID_SECTOR_CATEGORIES:
        add_error(errors, field, raw.get(field), f"Invalid sector. Allowed values: {', '.join(sorted(VALID_SECTOR_CATEGORIES))}")
        return value
    expected_sector = infer_sector_from_cn_code(cn_code) if cn_code else None
    if expected_sector and value != expected_sector:
        add_error(errors, field, raw.get(field), f"Sector Category does not match CN Code. Expected: {expected_sector}")
    return value


def validate_product_type(raw: dict[str, Any], errors: list[FieldError]) -> str | None:
    field = "Product Type"
    value = require_text(raw, field, errors)
    if value is None:
        return None
    normalized = value.strip().lower()
    allowed = {"simple": "Simple", "simple goods": "Simple", "complex": "Complex", "complex goods": "Complex"}
    if normalized not in allowed:
        add_error(errors, field, raw.get(field), "Allowed values are: Simple or Complex")
        return value
    return allowed[normalized]


def validate_positive_decimal(raw: dict[str, Any], field: str, errors: list[FieldError]) -> Decimal | None:
    value = raw.get(field)
    if is_blank(value):
        add_error(errors, field, value, "This field is required")
        return None
    try:
        decimal_value = Decimal(str(value).replace(",", ".").strip())
    except (InvalidOperation, AttributeError):
        add_error(errors, field, value, "Must be a valid decimal number")
        return None
    if decimal_value <= 0:
        add_error(errors, field, value, "Must be a positive number")
    return decimal_value


def validate_import_date(raw: dict[str, Any], errors: list[FieldError]) -> date | None:
    field = "Date of importation"
    value = raw.get(field)
    if is_blank(value):
        add_error(errors, field, value, "This field is required")
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    add_error(errors, field, value, "Must be a valid date. Accepted formats: DD.MM.YYYY, YYYY-MM-DD, DD/MM/YYYY")
    return None


def validate_country_of_origin(raw: dict[str, Any], errors: list[FieldError]) -> str | None:
    field = "Country of Origin"
    value = require_text(raw, field, errors)
    if value is None:
        return None
    country = pycountry.countries.get(alpha_2=value.upper()) or pycountry.countries.get(alpha_3=value.upper())
    if country is None:
        try:
            country = pycountry.countries.lookup(value)
        except LookupError:
            country = None
    if country is None:
        add_error(errors, field, raw.get(field), "Must match a valid ISO 3166-1 country")
        return value
    if country.alpha_2 in EXCLUDED_ORIGIN_ALPHA2:
        add_error(errors, field, raw.get(field), "Country of origin must be outside EU/exempt countries for CBAM scope")
    return country.name


def validate_record(raw: dict[str, Any]) -> tuple[dict[str, Any] | None, list[FieldError]]:
    """
    Valida una fila del Excel y devuelve los datos normalizados junto con los errores.
    Solo retorna un registro utilizable cuando todas las reglas pasan.
    """
    errors: list[FieldError] = []

    # Valida los campos en el mismo orden en que aparecen en el template.
    eori_number = validate_eori(raw, errors)
    declarant_legal_name = validate_non_empty_text(raw, "Declarant Legal Name", errors)
    declarant_address = validate_non_empty_text(raw, "Declarant Address", errors)
    contact_person = validate_contact_text(raw, "Contact Person", errors)
    competent_authority = validate_competent_authority(raw, errors)
    cbam_account_number = validate_non_empty_text(raw, "CBAM Account Number", errors)
    data_owner = validate_contact_text(raw, "Data Owner", errors)
    taric_code = validate_taric_code(raw, errors)
    cn_code = validate_cn_code(raw, errors)
    goods_description = validate_non_empty_text(raw, "Goods Description", errors)
    sector_category = validate_sector_category(raw, cn_code, errors)
    product_type = validate_product_type(raw, errors)
    import_volume = validate_positive_decimal(raw, "Import Volume", errors)
    date_of_importation = validate_import_date(raw, errors)
    country_of_origin = validate_country_of_origin(raw, errors)
    customs_declaration_ref = as_clean_string(raw.get("Customs Declaration Ref"))
    supplier_name = validate_non_empty_text(raw, "Supplier Name", errors)
    notes_comments = as_clean_string(raw.get("Notes / Comments"))

    if errors:
        return None, errors

    # Devuelve la fila lista para persistirse cuando no hay errores.
    sanitized = {
        "eori_number": eori_number,
        "declarant_legal_name": declarant_legal_name,
        "declarant_address": declarant_address,
        "contact_person": contact_person,
        "competent_authority": competent_authority,
        "cbam_account_number": cbam_account_number,
        "data_owner": data_owner,
        "taric_code": taric_code,
        "cn_code": cn_code,
        "goods_description": goods_description,
        "sector_category": sector_category,
        "product_type": product_type,
        "import_volume": import_volume,
        "date_of_importation": date_of_importation,
        "country_of_origin": country_of_origin,
        "customs_declaration_ref": customs_declaration_ref,
        "supplier_name": supplier_name,
        "notes_comments": notes_comments,
    }
    return sanitized, []
