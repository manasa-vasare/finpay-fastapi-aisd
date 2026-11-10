from sqlalchemy.orm import Session
from app.models import User


def get_by_id(db: Session, user_id: int):
    return db.get(User, user_id)


def get_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create(db: Session, name, email, password_hash, role):
    user = User(name=name, email=email, password_hash=password_hash, role=role)
    db.add(user)
    db.flush()
    return user
