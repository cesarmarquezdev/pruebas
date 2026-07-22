import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from database import Base, Usuario, get_session
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


"""/auth/register (POST → 201)
201 — registro válido, email nuevo → devuelve id y email
201 — el body devuelto NO trae hashed_password (verificar que UsuarioOut lo oculta)
409 — email ya registrado (registrar dos veces el mismo) → "El email ya esta registrado"
422 — email con formato inválido ("noesunemail") → EmailStr lo rechaza
422 — falta el campo password
422 — falta el campo email
""" ""


def test_registrovalido(client):
    r = client.post("/auth/register", json={"email": "b@b.com", "password": "4321"})
    assert r.status_code == 201


def test_nohashedpassword(client):
    r = client.post("/auth/register", json={"email": "b@b.com", "password": "1234"})
    assert r.status_code == 201
    r_json = r.json()
    assert "hashed_password" not in r_json


def test_registramos2veces(client):
    client.post("/auth/register", json={"email": "b@b.com", "password": "4321"})
    r = client.post("/auth/register", json={"email": "b@b.com", "password": "4321"})
    assert r.status_code == 409


def test_emailnovalido(client):
    r = client.post("/auth/register", json={"email": "bbb.com", "password": "4321"})
    assert r.status_code == 422


def test_faltaemail(client):
    r = client.post("/auth/register", json={"password": "4321"})
    assert r.status_code == 422


def test_faltapassword(client):
    r = client.post("/auth/register", json={"email": "b@b.com"})
    assert r.status_code == 422


"""/auth/login (POST → 200)
200 — credenciales correctas → devuelve access_token y token_type: "bearer"
401 — email existe pero password incorrecta → "Credenciales inválidas"
401 — email que no existe en la base → "Credenciales inválidas"
422 — falta email o password en el body"""


def test_credencialescorrectas(client):
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})
    r = client.post("/auth/login", json={"email": "a@a.com", "password": "1234"})
    assert r.status_code == 200


def test_emailexitepasswordno(client):
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})
    r = client.post("/auth/login", json={"email": "a@a.com", "password": "1235"})
    assert r.status_code == 401


def test_emailnoexiste(client):
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})
    r = client.post("/auth/login", json={"email": "b@a.com", "password": "1235"})
    assert r.status_code == 401


def test_faltaemail2(client):
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})
    r = client.post("/auth/login", json={"password": "1235"})
    assert r.status_code == 422


"""
/auth/me (GET → 200)
200 — con token válido → devuelve el usuario logueado
401 — token inválido / manipulado → "Token inválido"
401 — sin header Authorization → 401/403 (HTTPBearer lo bloquea)
401 — token válido en forma pero de un usuario borrado (sub apunta a id inexistente)
"""


def test_obtener_perfil_usuario_logueado(client):
    # 1. Registro: Creamos el usuario en la base de datos vacía
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})

    # 2. Login: Obtenemos el token de acceso
    r = client.post("/auth/login", json={"email": "a@a.com", "password": "1234"})
    assert r.status_code == 200

    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Petición a /auth/me: Enviamos el token en la cabecera
    r = client.get("/auth/me", headers=headers)

    # 4. Aserciones: Validamos que responda 200 y devuelva los datos correctos
    assert r.status_code == 200


def test_tokeninvalido(client):
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})
    r = client.post("/auth/login", json={"email": "a@a.com", "password": "1234"})
    assert r.status_code == 200

    token_trucho = 1
    headers = {"Authorization": f"Bearer {token_trucho}"}
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 401


def test_sinheader(client):
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})
    r = client.post("/auth/login", json={"email": "a@a.com", "password": "1234"})
    assert r.status_code == 200

    r = client.get("/auth/me")
    assert r.status_code == 401


def test_tokenborrado(client):
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})

    # 2. Login: Obtenemos el token de acceso
    r = client.post("/auth/login", json={"email": "a@a.com", "password": "1234"})
    assert r.status_code == 200

    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Petición a /auth/me: Enviamos el token en la cabecera
    r = client.get("/auth/me", headers=headers)

    # 4. Aserciones: Validamos que responda 200 y devuelva los datos correctos
    assert r.status_code == 200


def test_token_valido_pero_usuario_eliminado(client):
    # 1. Registro y Login (Lo que ya sabes hacer)
    client.post("/auth/register", json={"email": "borrado@a.com", "password": "1234"})
    r = client.post("/auth/login", json={"email": "borrado@a.com", "password": "1234"})

    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    session = app.dependency_overrides[get_session]()
    usuario = session.scalars(
        select(Usuario).where(Usuario.email == "borrado@a.com")
    ).first()

    # 2. BORRAR EL USUARIO usando la API
    # Suponiendo que tienes una ruta para eliminar al usuario autenticado:
    session.delete(usuario)
    session.commit()  # dentro del test, no en router.py
    # O tal vez: client.delete("/usuarios/mi-id", headers=headers)

    # 3. Intentar acceder a /auth/me con el token del usuario que ya no existe
    r = client.get("/auth/me", headers=headers)

    # 4. Aserciones
    # Tu API debería fallar aquí porque el token es válido (no ha expirado),
    # pero al buscar el ID en la BD, no va a encontrar nada.
    assert r.status_code == 401  # O 404, dependiendo de cómo manejes el error


"""
/notas POST (crear → 201)
201 — nota válida con token → devuelve titulo, id, usuario_id
401 — crear nota sin token
422 — falta titulo o nota en el body
201 — la nota queda asociada al usuario_id correcto (el del token)""" ""


def test_notavalida(client):
    re = client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})
    r = client.post("/auth/login", json={"email": "a@a.com", "password": "1234"})
    user_id = re.json()["id"]
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/notas", json={"titulo": "NotaCesar", "nota": "Hola mUNDO"}, headers=headers
    )
    assert r.status_code == 201
    assert r.json()["titulo"] == "NotaCesar"
    assert r.json()["usuario_id"] == user_id


def test_notasintoken(client):

    re = client.post("/notas", json={"titulo": "NotaCesar", "nota": "Hola mUNDO"})
    assert re.status_code == 401


def test_sintituloenbody(client):
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
        json={"nota": "Hola mundo"},
        headers=headers,
    )

    # 201 = creada. Y comprobamos que el body devuelto es el que esperamos.
    assert r.status_code == 422


"""
/notas GET (listar → 200)
200 — usuario con notas → lista con la cantidad correcta
200 — usuario sin notas → lista vacía []
200 — solo devuelve MIS notas, no las de otro usuario (aislamiento)
401 — listar sin token"""


def test_usuarioconnotas(client):
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


def test_usuariosinnotas(client):
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
    r = client.get("/notas", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 0


def test_sololasmias(client):
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


def test_listar_sintoken(client):

    r = client.get("/notas")
    assert r.status_code == 401


"""
/notas/{id} GET (ver una → 200)
200 — ver mi propia nota
404 — nota que no existe (id inventado)
403 — ver la nota de OTRO usuario
401 — sin token""" ""


def test_vernota(client):
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
    nota_id = r.json()["id"]
    r = client.get(f"/notas/{nota_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["id"] == nota_id


def test_idinventado(client):
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})
    r = client.post("/auth/login", json={"email": "a@a.com", "password": "1234"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/notas",
        json={"titulo": "Mi primera nota", "nota": "Hola mundo"},
        headers=headers,
    )
    assert r.status_code == 201
    nota_id_invent = 99
    r = client.get(f"/notas/{nota_id_invent}", headers=headers)
    assert r.status_code == 404


"""

/notas/{id} PATCH (editar → 200)
200 — editar solo titulo (el nota queda igual)
200 — editar solo nota (el titulo queda igual)
200 — editar ambos campos
200 — body vacío {} → no cambia nada (todos los campos None)
404 — editar nota inexistente
403 — editar nota de otro usuario
401 — sin token""" ""


def test_editar_titulo(client):
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
    nota_id = r.json()["id"]
    r = client.get(f"/notas/{nota_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["id"] == nota_id
    r = client.patch(
        f"/notas/{nota_id}", json={"titulo": "Titulo nuevo"}, headers=headers
    )
    assert r.status_code == 200
    assert r.json()["titulo"] == "Titulo nuevo"


def test_editar_ntoa(client):
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
    nota_id = r.json()["id"]
    r = client.get(f"/notas/{nota_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["id"] == nota_id
    r = client.patch(f"/notas/{nota_id}", json={"nota": "nota nuevo"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["nota"] == "nota nuevo"


def test_editarnotainexistente(client):
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})
    r = client.post("/auth/login", json={"email": "a@a.com", "password": "1234"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/notas",
        json={"titulo": "Mi primera nota", "nota": "Hola mundo"},
        headers=headers,
    )
    nota_id_invent = 99
    r = client.patch(
        f"/notas/{nota_id_invent}", json={"nota": "nota nuevo"}, headers=headers
    )
    assert r.status_code == 404


def test_notadeotro(client):
    # --- Usuario A crea la nota ---
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})
    token_a = client.post(
        "/auth/login", json={"email": "a@a.com", "password": "1234"}
    ).json()["access_token"]
    r = client.post(
        "/notas",
        json={"titulo": "de A", "nota": "..."},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    nota_id = r.json()["id"]
    # --- Usuario B intenta editarla ---
    client.post("/auth/register", json={"email": "b@b.com", "password": "4321"})
    token_b = client.post(
        "/auth/login", json={"email": "b@b.com", "password": "4321"}
    ).json()["access_token"]
    r = client.patch(
        f"/notas/{nota_id}",
        json={"titulo": "hackeado"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r.status_code == 403


"""
/notas/{id} DELETE (borrar → 204)
204 — borrar mi propia nota (y confirmar que luego da 404 al buscarla)
404 — borrar nota inexistente
403 — borrar nota de otro usuario
401 — sin token"""


def test_borrar_mi_nota(client):
    # Registro + login
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})
    token = client.post(
        "/auth/login", json={"email": "a@a.com", "password": "1234"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # Creo la nota y capturo su id
    nota_id = client.post(
        "/notas", json={"titulo": "X", "nota": "Y"}, headers=headers
    ).json()["id"]
    # Borro → 204
    r = client.delete(f"/notas/{nota_id}", headers=headers)
    assert r.status_code == 204
    # Confirmo que ya no existe → 404
    r = client.get(f"/notas/{nota_id}", headers=headers)
    assert r.status_code == 404


def test_borrar_nota_inexistente(client):
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})
    token = client.post(
        "/auth/login", json={"email": "a@a.com", "password": "1234"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.delete("/notas/9999", headers=headers)  # id que nunca existió
    assert r.status_code == 404


def test_borrar_nota_de_otro(client):
    # Usuario A crea la nota
    client.post("/auth/register", json={"email": "a@a.com", "password": "1234"})
    token_a = client.post(
        "/auth/login", json={"email": "a@a.com", "password": "1234"}
    ).json()["access_token"]
    nota_id = client.post(
        "/notas",
        json={"titulo": "de A", "nota": "Y"},
        headers={"Authorization": f"Bearer {token_a}"},
    ).json()["id"]
    # Usuario B intenta borrarla
    client.post("/auth/register", json={"email": "b@b.com", "password": "4321"})
    token_b = client.post(
        "/auth/login", json={"email": "b@b.com", "password": "4321"}
    ).json()["access_token"]
    r = client.delete(
        f"/notas/{nota_id}", headers={"Authorization": f"Bearer {token_b}"}
    )
    assert r.status_code == 403


def test_borrar_sin_token(client):
    r = client.delete("/notas/1")  # sin headers → nunca me autentico
    assert r.status_code == 401  # HTTPBearer frena por falta de header
