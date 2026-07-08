from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """
    Base comun para todos los modelos ORM del proyecto.
    """
    pass


settings = get_settings()
engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    """
    Crea las tablas definidas por los modelos cuando la API arranca.
    """
    # Importa los modelos antes de crear las tablas.
    from app.models.record import CBAMRecord  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Entrega una sesion de base de datos por solicitud y la cierra al final.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
