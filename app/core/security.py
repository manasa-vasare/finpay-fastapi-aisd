import os, hmac, hashlib, secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import AppError
from app.repositories import user_repository

SECRET = os.getenv("FINPAY_SECRET", "finpay-dev-secret-change-me-please-32b")
bearer = HTTPBearer()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    salt, digest = stored.split("$")
    check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return hmac.compare_digest(check, digest)


def create_token(user_id: int, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=8),
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    try:
        data = jwt.decode(creds.credentials, SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise AppError("Invalid or expired token", 401)
    user = user_repository.get_by_id(db, int(data["sub"]))
    if not user:
        raise AppError("User not found", 401)
    return user


def require_role(*roles):
    def checker(user=Depends(current_user)):
        if user.role not in roles:
            raise AppError(f"Access denied for role '{user.role}'", 403)
        return user

    return checker
