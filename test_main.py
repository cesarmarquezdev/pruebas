import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from database import Base, get_session
from main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        app.dependency_overrides[get_session] = lambda: session
        yield TestClient(app)
        app.dependency_overrides.clear()


def test_crear_nota(client):
    # Registro: creamos el usuario. La base está vacía en cada test,
    # así que este email nunca choca con nada.
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})

    # Login: le mandamos las mismas credenciales y nos devuelve el token.
    r = client.post("/auth/login", json={"email": "a@a.com", "password": "1234"})
    assert r.status_code == 200

    # El body del login es {"access_token": "...", "token_type": "bearer"}.
    # r.json() lo convierte en dict y sacamos la clave que nos interesa.
    token = r.json()["access_token"]

    # Esta cabecera es el equivalente al botón "Authorize" de Swagger.
    headers = {"Authorization": f"Bearer {token}"}

    # Ahora sí, la nota. Los campos son los de NotaIn: titulo y nota.
    r = client.post(
        "/notas",
        json={"titulo": "Mi primera nota", "nota": "Hola mundo"},
        headers=headers,
    )

    # 201 = creada. Y comprobamos que el body devuelto es el que esperamos.
    assert r.status_code == 201
    assert r.json()["titulo"] == "Mi primera nota"


def test_listar_notas(client):
    # Registro: creamos el usuario. La base está vacía en cada test,
    # así que este email nunca choca con nada.
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})

    # Login: le mandamos las mismas credenciales y nos devuelve el token.
    r = client.post("/auth/login", json={"email": "a@a.com", "password": "1234"})
    assert r.status_code == 200

    # El body del login es {"access_token": "...", "token_type": "bearer"}.
    # r.json() lo convierte en dict y sacamos la clave que nos interesa.
    token = r.json()["access_token"]

    # Esta cabecera es el equivalente al botón "Authorize" de Swagger.
    headers = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/notas",
        json={"titulo": "Mi primera nota de cesar", "nota": "Hola mundo cesar"},
        headers=headers,
    )
    r = client.get("/notas", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_no_puedo_ver_notas_de_otro(client):
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})
    r = client.post("/auth/login", json={"email": "a@a.com", "password": "1234"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/notas",
        json={
            "titulo": "Mi primer test nota de cesar",
            "nota": "Hola mundo cesar test",
        },
        headers=headers,
    )
    nota_id = r.json()["id"]
    client.post("/auth/register", json={"email": "b@b.com", "password": "4321"})
    r = client.post("/auth/login", json={"email": "b@b.com", "password": "4321"})
    assert r.status_code == 200
    token_b = r.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    r = client.get(f"/notas/{nota_id}", headers=headers_b)
    assert r.status_code == 403
