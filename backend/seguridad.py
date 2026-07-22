import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("JWT_SECRET", "")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))


def crear_token(usuario_id: int) -> str:
    payload = {
        "sub": str(usuario_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")
