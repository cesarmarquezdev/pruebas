from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Nota(Base):
    __tablename__ = "notas"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column()
    nota: Mapped[str] = mapped_column()


engine = create_engine("sqlite:///notas.db", echo=True)

Base.metadata.create_all(bind=engine)
