from sqlalchemy.orm import Session
from app.models import Merchant


def create(db: Session, user_id, business_name, category):
    merchant = Merchant(user_id=user_id, business_name=business_name, category=category)
    db.add(merchant)
    db.flush()
    return merchant


def get(db: Session, merchant_id: int):
    return db.get(Merchant, merchant_id)


def get_by_user(db: Session, user_id: int):
    return db.query(Merchant).filter(Merchant.user_id == user_id).first()


def list_all(db: Session):
    return db.query(Merchant).all()
