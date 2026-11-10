from sqlalchemy.orm import Session
from app.core.errors import AppError
from app.repositories import merchant_repository

CATEGORY_MAP = {
    "CANTEEN": "CANTEEN",
    "FOOD": "CANTEEN",
    "CAFE": "CANTEEN",
    "STATIONERY": "STATIONERY",
    "BOOKS": "STATIONERY",
    "BOOKSTORE": "STATIONERY",
    "TRANSPORT": "TRANSPORT",
    "TRAVEL": "TRANSPORT",
    "BUS": "TRANSPORT",
    "HOSTEL": "HOSTEL",
    "MESS": "HOSTEL",
    "ONLINE": "ONLINE",
    "GENERAL": "CANTEEN",
}


def normalize_category(category: str) -> str:
    cleaned = (category or "").strip().upper()
    return CATEGORY_MAP.get(cleaned, "CANTEEN")


def register(db: Session, user, data):
    if merchant_repository.get_by_user(db, user.id):
        raise AppError("Merchant profile already exists for this user", 400)
    category = normalize_category(data.category)
    merchant = merchant_repository.create(db, user.id, data.business_name, category)
    db.commit()
    db.refresh(merchant)
    return merchant


def get_or_404(db: Session, merchant_id: int):
    merchant = merchant_repository.get(db, merchant_id)
    if not merchant:
        raise AppError("Merchant not found", 404)
    return merchant


def my_profile(db: Session, user):
    merchant = merchant_repository.get_by_user(db, user.id)
    if not merchant:
        raise AppError("Create your merchant profile first", 404)
    return merchant


def list_all(db: Session):
    return merchant_repository.list_all(db)
