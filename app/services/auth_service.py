from sqlalchemy.orm import Session
from app.core.errors import AppError
from app.core.security import hash_password, verify_password, create_token
from app.repositories import user_repository, wallet_repository

ROLES = {"student", "merchant", "admin"}


def register(db: Session, data):
    if data.role not in ROLES:
        raise AppError(f"Role must be one of {sorted(ROLES)}")
    if user_repository.get_by_email(db, data.email):
        raise AppError("Email already registered")
    user = user_repository.create(db, data.name, data.email, hash_password(data.password), data.role)
    if user.role == "student":
        wallet_repository.create_wallet(db, user.id)  # every student gets a wallet
    db.commit()
    return user


def login(db: Session, data):
    user = user_repository.get_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise AppError("Invalid email or password", 401)
    return {"access_token": create_token(user.id, user.role), "token_type": "bearer", "role": user.role}
