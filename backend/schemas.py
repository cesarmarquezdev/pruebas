from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr


class Editarnota(BaseModel):
    titulo: str | None = None
    nota: str | None = None


class Crearnota(BaseModel):
    titulo: str
    nota: str


class NotaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    nota: str
    usuario_id: int
    creation_date: datetime
    modification_date: datetime


class NotaIn(BaseModel):
    titulo: str
    nota: str


class NotaListItem(BaseModel):
    """Metadatos de la nota para el listado paginado (sin contenido)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    modification_date: datetime
