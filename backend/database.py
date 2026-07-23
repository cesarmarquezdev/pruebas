import os
from collections.abc import Generator
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import DateTime, ForeignKey, String, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

load_dotenv()
URL = os.getenv("DATABASE_URL", "postgresql+psycopg://notas:notas@localhost:5432/notas")


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

engine = create_engine(URL, echo=True)

Base.metadata.create_all(bind=engine)

# --- 4. SESIÓN POR PETICIÓN (dependencia de FastAPI) ---


def get_session() -> Generator[Session, None, None]:
    with Session(bind=engine) as session:
        yield session
