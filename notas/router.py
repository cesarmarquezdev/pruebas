from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from classes import Editarnota, NotaIn, NotaListItem, NotaOut
from database import Nota
from deps import SessionDep, UsuarioActual

router = APIRouter(prefix="/notas", tags=["notas"])


@router.post("", status_code=201, response_model=NotaOut)
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


@router.delete("/{id}", status_code=204)
def eliminar_nota(usuario: UsuarioActual, id: int, session: SessionDep) -> None:
    consulta = select(Nota).where(Nota.id == id)
    nota = session.scalars(consulta).first()
    if nota is None:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    if nota.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    session.delete(nota)
    session.commit()


@router.patch("/{id}", response_model=NotaOut)
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


@router.get("/{id}", response_model=NotaOut)
def mostrar_nota(usuario: UsuarioActual, id: int, session: SessionDep):
    consulta = select(Nota).where(Nota.id == id)
    nota = session.scalars(consulta).first()

    if nota is None:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    if nota.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    return nota


@router.get("")
def notas_list(
    usuario: UsuarioActual,
    session: SessionDep,
    skip: int = 0,
    limit: int = 20,
) -> list[NotaListItem]:
    """Lista paginada de las notas del usuario (solo metadatos, sin contenido)."""
    consulta = (
        select(Nota)
        .where(Nota.usuario_id == usuario.id)
        .offset(skip)
        .limit(limit)
    )
    notas = session.scalars(consulta).all()
    return [NotaListItem.model_validate(n) for n in notas]
