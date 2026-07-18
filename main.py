from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext

from notas.router import router as notas_router
from usuarios.router import router as usuarios_router

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app.include_router(usuarios_router)
app.include_router(notas_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ← tú decides qué va aquí
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}
