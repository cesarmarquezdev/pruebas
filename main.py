from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import cargar_db, guardar_db

app = FastAPI()


class Editarnota(BaseModel):
    titulo: str | None = None
    nota: str | None = None


class Crearnota(BaseModel):
    titulo: str
    nota: str


@app.get("/notas")
def notas_list() -> list[dict]:
    """Es una funcion que usamos para listar nuestra base de datos."""
    db = cargar_db()
    return db["notas"]


@app.post("/notas")
def crear_notas(nota: Crearnota) -> dict:
    """Es una funcion que usamos para
    cargar la base de datos.
    y guardar una nueva nota en ella."""
    db = cargar_db()
    db["notas"].append(nota.model_dump())
    guardar_db(db)
    return {"mensaje": "Nota creada con éxito", "datos": nota}


@app.delete("/notas/{titulo}")
def eliminar_nota(titulo: str) -> dict:
    """Una funcion que elimina una nota
    Creamos una lista nueva dejando afuera la nota
    que deseamos borrar."""
    db = cargar_db()
    total_antes = len(db["notas"])
    db["notas"] = [u for u in db["notas"] if u["titulo"] != titulo]
    if len(db["notas"]) < total_antes:
        guardar_db(db)
        return {"mensaje": " borrado con éxito!", "datos": titulo}
    else:
        raise HTTPException(status_code=404, detail="Elemento no encontrado")


@app.patch("/notas/{titulo}")
def editar_notas(titulo: str, cambios: Editarnota) -> dict:
    """Una función que actualiza parcialmente una nota existente.
    Solo modifica los campos que no sean None en el body."""
    db = cargar_db()

    # Variable para rastrear si encontramos la nota (y para devolverla al final)
    nota_actualizada = None

    for item in db["notas"]:
        if item["titulo"] == titulo:
            # 1. Revisar si cambios.titulo no es None, y si no lo es, actualizar
            if cambios.titulo is not None:
                item["titulo"] = cambios.titulo

            # 2. Revisar si cambios.nota no es None, y si no lo es, actualizar
            if cambios.nota is not None:
                item["nota"] = cambios.nota

            # Guardamos la referencia de que SÍ la encontramos
            nota_actualizada = item
            # 3. break para no seguir buscando en vano
            break

    # Después del for: ¿La encontramos?
    if nota_actualizada is None:
        raise HTTPException(status_code=404, detail="Nota no encontrada")

    # Si llegamos aquí, sí existía y ya fue modificada en la memoria
    guardar_db(db)
    return {"mensaje": "Nota editada con éxito!", "datos": nota_actualizada}
