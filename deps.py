from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Usuario, get_session
from seguridad import SECRET

SessionDep = Annotated[Session, Depends(get_session)]

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
