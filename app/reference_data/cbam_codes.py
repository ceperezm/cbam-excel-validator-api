"""Prefijos y reglas simplificadas para clasificar codigos CN dentro del alcance CBAM."""

CBAM_CN_PREFIXES_BY_SECTOR = {
    "Iron and Steel": ("72", "7301", "7302", "7303", "7304", "7305", "7306", "7307", "7308"),
    "Aluminium": ("7601", "7603", "7604", "7605", "7606", "7607", "7608"),
    "Cement": ("2507", "2523"),
    "Fertilisers": ("2808", "2814", "3102", "3105"),
    "Electricity": ("2716",),
    "Hydrogen": ("280410",),
}

VALID_SECTOR_CATEGORIES = set(CBAM_CN_PREFIXES_BY_SECTOR)


def infer_sector_from_cn_code(cn_code: str) -> str | None:
    for sector, prefixes in CBAM_CN_PREFIXES_BY_SECTOR.items():
        if any(cn_code.startswith(prefix) for prefix in prefixes):
            return sector
    return None


def is_cbam_annex_i_code(cn_code: str) -> bool:
    return infer_sector_from_cn_code(cn_code) is not None
