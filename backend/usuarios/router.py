import bcrypt
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from classes import UsuarioIn, UsuarioOut
from database import Usuario
from deps import SessionDep, UsuarioActual
from seguridad import crear_token

router = APIRouter(prefix="/auth", tags=["auth"])


def hashear(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verificar(plano: str, hasheado: str) -> bool:
    return bcrypt.checkpw(plano.encode(), hasheado.encode())


@router.post("/register", status_code=201, response_model=UsuarioOut)
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


@router.post("/login", status_code=200)
def autentificacion_usuario(datos: UsuarioIn, session: SessionDep):
    consulta_usuario = select(Usuario).where(Usuario.email == datos.email)
    usuario = session.scalars(consulta_usuario).first()
    if usuario is None or not verificar(datos.password, usuario.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"access_token": crear_token(usuario.id), "token_type": "bearer"}


@router.get("/me", response_model=UsuarioOut)
def leer_usuario_actual(usuario: UsuarioActual) -> Usuario:
    return usuario
