from fastapi import FastAPI
from passlib.context import CryptContext

from notas.router import router as notas_router
from usuarios.router import router as usuarios_router

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app.include_router(usuarios_router)
app.include_router(notas_router)


@app.get("/health")
def health():
    return {"status": "ok"}
