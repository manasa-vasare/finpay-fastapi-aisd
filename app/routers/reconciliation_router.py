from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app.services import reconciliation_service

router = APIRouter(prefix="/reconciliation", tags=["Monthly Reconciliation"])


@router.get("/monthly")
def monthly(year: int, month: int, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    return reconciliation_service.monthly_report(db, year, month)
