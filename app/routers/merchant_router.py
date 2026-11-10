from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, current_user
from app.schemas import MerchantIn, MerchantOut
from app.services import merchant_service

router = APIRouter(prefix="/merchants", tags=["Merchants"])


@router.post("", response_model=MerchantOut, status_code=201)
def register_merchant(data: MerchantIn, user=Depends(require_role("merchant")), db: Session = Depends(get_db)):
    return merchant_service.register(db, user, data)


@router.get("", response_model=List[MerchantOut])
def list_merchants(user=Depends(current_user), db: Session = Depends(get_db)):
    return merchant_service.list_all(db)


@router.get("/me", response_model=MerchantOut)
def my_profile(user=Depends(require_role("merchant")), db: Session = Depends(get_db)):
    return merchant_service.my_profile(db, user)
