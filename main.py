from datetime import datetime
from typing import Annotated

import bcrypt
from fastapi import Depends, FastAPI, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import Nota, Usuario, get_session

SessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# hashear:  pwd_context.hash(password)
# verificar: pwd_context.verify(plano, hash)   ← para el login, mañana


class UsuarioIn(BaseModel):
    email: EmailStr
    password: str


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


def hashear(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verificar(plano: str, hasheado: str) -> bool:
    return bcrypt.checkpw(plano.encode(), hasheado.encode())


@app.post("/auth/register", status_code=201, response_model=UsuarioOut)
def registro_usuario(datos: UsuarioIn, session: SessionDep) -> Usuario:
    usuario = Usuario(
        email=datos.email,
        hashed_password=hashear(datos.password),
    )
    session.add(usuario)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="El email ya esta esta registrado")

    session.refresh(usuario)
    return usuario


@app.get("/notas")
def notas_list(session: SessionDep) -> list[NotaOut]:
    """Lista todas las notas desde SQLite."""
    notas = session.scalars(select(Nota)).all()
    return [NotaOut.model_validate(n) for n in notas]


class NotaIn(BaseModel):
    titulo: str
    nota: str


USUARIO_TEMPORAL = 1  # TODO: reemplazar por el usuario del token (Fase 3c)


@app.post("/notas", status_code=201, response_model=NotaOut)
def crear_nota(datos: NotaIn, session: SessionDep) -> Nota:
    nota = Nota(
        titulo=datos.titulo,
        nota=datos.nota,
        usuario_id=USUARIO_TEMPORAL,
    )
    session.add(nota)
    session.commit()
    session.refresh(nota)
    return nota


@app.delete("/notas/{id}", status_code=204)
def eliminar_nota(id: int, session: SessionDep) -> None:
    """Una funcion que elimina una nota
    Creamos una lista nueva dejando afuera la nota
    que deseamos borrar."""
    consulta = select(Nota).where(Nota.id == id)
    nota = session.scalars(consulta).first()
    if nota is None:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    session.delete(nota)
    session.commit()


@app.patch("/notas/{id}", response_model=NotaOut)
def editar_notas(id: int, datos: Editarnota, session: SessionDep) -> Nota:
    """Una función que actualiza parcialmente una nota existente.
    Solo modifica los campos que no sean None en el body."""
    consulta = select(Nota).where(Nota.id == id)
    nota = session.scalars(consulta).first()
    if nota is None:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    if datos.titulo is not None:
        "aqui como se que tengo que actualizar con lo que me llego ? "
        nota.titulo = datos.titulo
    if datos.nota is not None:
        nota.nota = datos.nota
    session.commit()
    session.refresh(nota)
    return nota
