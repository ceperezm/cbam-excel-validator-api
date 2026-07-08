from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Agrupa la configuracion base que la API lee desde variables de entorno.
    """
    app_name: str = "CBAM Excel Validator API"
    database_url: str = "postgresql+psycopg2://cbam:cbam@db:5432/cbam"
    max_upload_size_mb: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """
    Carga la configuracion una sola vez para reutilizarla en toda la aplicacion.
    """
    return Settings()
