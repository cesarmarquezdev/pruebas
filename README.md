# Notas API

App de notas con autenticación: backend en FastAPI + PostgreSQL, frontend en React (Vite).

## Correr todo con Docker

Requiere [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
docker compose up -d --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000 (docs interactivas en http://localhost:8000/docs)
- Postgres: localhost:5432 (user/pass/db: `notas`/`notas`/`notas`)

Para bajar todo: `docker compose down` (agrega `-v` si además quieres borrar los datos de Postgres).

## Desarrollo sin Docker

Backend (requiere Postgres corriendo aparte, o solo el servicio `db`: `docker compose up -d db`):

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```
