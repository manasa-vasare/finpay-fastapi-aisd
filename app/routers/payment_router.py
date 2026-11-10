from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app.schemas import PaymentIn, TransactionOut
from app.services import payment_service

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("", response_model=TransactionOut, status_code=201)
def make_payment(data: PaymentIn, user=Depends(require_role("student")), db: Session = Depends(get_db)):
    return payment_service.pay(
        db,
        student=user,
        merchant_id=data.merchant_id,
        amount=data.amount,
        amount_paise=data.amount_paise,
        idempotency_key=data.idempotency_key
    )


@router.get("/history", response_model=List[TransactionOut])
def my_payments(user=Depends(require_role("student")), db: Session = Depends(get_db)):
    return payment_service.student_history(db, user.id)


@router.get("/received", response_model=List[TransactionOut])
def received_payments(user=Depends(require_role("merchant")), db: Session = Depends(get_db)):
    return payment_service.merchant_history(db, user)
