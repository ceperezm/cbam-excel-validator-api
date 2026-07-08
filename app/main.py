from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api import records, upload
from app.core.config import get_settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Inicializa las tablas de la base de datos antes de atender peticiones.
    """
    init_db()
    yield


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="API para cargar, validar, guardar y consultar registros CBAM desde archivos Excel.",
    lifespan=lifespan,
)

app.include_router(upload.router)
app.include_router(records.router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """
    Expone una verificacion simple para confirmar que la API esta activa.
    """
    return {"status": "ok"}
