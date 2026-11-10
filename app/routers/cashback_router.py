from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, current_user
from app.schemas import CashbackOut
from app.services import cashback_service, wallet_service

router = APIRouter(prefix="/cashback", tags=["Cashback"])


@router.get("/rules")
def get_rules(user=Depends(current_user)):
    return cashback_service.rules()


@router.get("/history", response_model=List[CashbackOut])
def history(user=Depends(require_role("student")), db: Session = Depends(get_db)):
    wallet = wallet_service.get_wallet(db, user.id)
    return cashback_service.history(db, wallet.id)
