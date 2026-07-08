"""Listado minimo de paises excluidos para la validacion de origen de mercancias."""

EU_COUNTRY_ALPHA2 = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE",
    "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT",
    "RO", "SK", "SI", "ES", "SE",
}

CBAM_EXEMPT_ALPHA2 = {
    "IS", "LI", "NO", "CH",
}

EXCLUDED_ORIGIN_ALPHA2 = EU_COUNTRY_ALPHA2 | CBAM_EXEMPT_ALPHA2
