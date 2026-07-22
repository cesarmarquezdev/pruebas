from collections.abc import Generator
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, create_engine, event, func
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

# --- 1. ACTIVAR FOREIGN KEYS EN SQLITE ---

# Este bloque intercepta cada conexión a SQLite y le dice al guardia que despierte.


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):

    cursor = dbapi_connection.cursor()

    cursor.execute("PRAGMA foreign_keys=ON")

    cursor.close()


# --- 2. DECLARACIÓN DE MODELOS ---


class Base(DeclarativeBase):
    pass


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(String(255), unique=True)

    hashed_password: Mapped[str] = mapped_column(String(255))


class Nota(Base):
    __tablename__ = "notas"

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))

    id: Mapped[int] = mapped_column(primary_key=True)

    titulo: Mapped[str] = mapped_column()

    nota: Mapped[str] = mapped_column()

    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    modification_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# --- 3. CONFIGURACIÓN E INICIALIZACIÓN ---

engine = create_engine("sqlite:///notas.db", echo=True)

Base.metadata.create_all(bind=engine)

# --- 4. SESIÓN POR PETICIÓN (dependencia de FastAPI) ---


def get_session() -> Generator[Session, None, None]:
    with Session(bind=engine) as session:
        yield session
