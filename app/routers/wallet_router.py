from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app.schemas import TopupIn, BalanceOut, LedgerOut, TierUpdateIn
from app.services import wallet_service

router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.get("/balance", response_model=BalanceOut)
def balance(user=Depends(require_role("student")), db: Session = Depends(get_db)):
    return wallet_service.get_balance(db, user.id)


@router.post("/topup", response_model=BalanceOut)
def topup(data: TopupIn, user=Depends(require_role("student")), db: Session = Depends(get_db)):
    return wallet_service.topup(db, user.id, amount=data.amount, amount_paise=data.amount_paise)


@router.post("/tier", response_model=BalanceOut)
def update_tier(data: TierUpdateIn, user=Depends(require_role("student")), db: Session = Depends(get_db)):
    return wallet_service.set_tier(db, user.id, data.tier)


@router.get("/history", response_model=List[LedgerOut])
def history(user=Depends(require_role("student")), db: Session = Depends(get_db)):
    return wallet_service.history(db, user.id)
