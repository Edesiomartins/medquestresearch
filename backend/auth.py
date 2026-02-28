"""
Autenticação: criação de JWT e obtenção do usuário atual a partir do header Authorization.
"""

import os
from datetime import datetime, timedelta

from fastapi import Header, HTTPException
from jose import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_hours: int = 12):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=expires_hours)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Não autorizado")

    if authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "").strip()
    else:
        token = authorization.strip()

    if not token:
        raise HTTPException(status_code=401, detail="Não autorizado")

    try:
        from backend.database import db_select_one
    except ImportError:
        try:
            from database import db_select_one
        except ImportError:
            from .database import db_select_one

    row = db_select_one("SELECT * FROM usuarios WHERE token = %s", (token,))
    if not row:
        raise HTTPException(status_code=401, detail="Não autorizado")
    return dict(row)
