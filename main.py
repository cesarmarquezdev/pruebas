from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from classes import Editarnota, NotaIn, NotaOut, UsuarioIn, UsuarioOut
from database import Nota, Usuario, get_session
from seguridad import SECRET, crear_token

SessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


security = HTTPBearer()


def get_current_user(
    credenciales: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: SessionDep,
) -> Usuario:
    try:
        payload = jwt.decode(credenciales.credentials, SECRET, algorithms=["HS256"])
        usuario_id = int(payload["sub"])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

    usuario = session.scalars(select(Usuario).where(Usuario.id == usuario_id)).first()
    if usuario is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    return usuario


UsuarioActual = Annotated[Usuario, Depends(get_current_user)]


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


@app.post("/notas", status_code=201, response_model=NotaOut)
def crear_nota(usuario: UsuarioActual, datos: NotaIn, session: SessionDep) -> Nota:
    nota = Nota(
        titulo=datos.titulo,
        nota=datos.nota,
        usuario_id=usuario.id,
    )
    session.add(nota)
    session.commit()
    session.refresh(nota)
    return nota


@app.post("/auth/login", status_code=200)
def autentificacion_usuario(datos: UsuarioIn, session: SessionDep):
    consulta_usuario = select(Usuario).where(Usuario.email == datos.email)
    usuario = session.scalars(consulta_usuario).first()
    if usuario is None or not verificar(datos.password, usuario.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"access_token": crear_token(usuario.id), "token_type": "bearer"}


@app.delete("/notas/{id}", status_code=204)
def eliminar_nota(usuario: UsuarioActual, id: int, session: SessionDep) -> None:
    consulta = select(Nota).where(Nota.id == id)
    nota = session.scalars(consulta).first()
    if nota is None:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    if nota.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    session.delete(nota)
    session.commit()


@app.patch("/notas/{id}", response_model=NotaOut)
def editar_notas(
    usuario: UsuarioActual, id: int, datos: Editarnota, session: SessionDep
) -> Nota:
    """Una función que actualiza parcialmente una nota existente.
    Solo modifica los campos que no sean None en el body."""
    consulta = select(Nota).where(Nota.id == id)
    nota = session.scalars(consulta).first()

    if nota is None:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    if nota.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    if datos.titulo is not None:
        nota.titulo = datos.titulo
    if datos.nota is not None:
        nota.nota = datos.nota
    session.commit()
    session.refresh(nota)
    return nota


@app.get("/auth/me", response_model=UsuarioOut)
def leer_usuario_actual(usuario: UsuarioActual) -> Usuario:
    return usuario


@app.get("/notas/{id}", response_model=NotaOut)
def mostrar_nota(usuario: UsuarioActual, id: int, session: SessionDep):
    consulta = select(Nota).where(Nota.id == id)
    nota = session.scalars(consulta).first()

    if nota is None:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    if nota.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    return nota


@app.get("/notas")
def notas_list(usuario: UsuarioActual, session: SessionDep) -> list[NotaOut]:
    """Lista todas las notas desde SQLite."""
    consulta = select(Nota).where(Nota.usuario_id == usuario.id)
    notas = session.scalars(consulta).all()
    return [NotaOut.model_validate(n) for n in notas]
