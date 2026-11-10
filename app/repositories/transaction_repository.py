from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Transaction, Merchant


def get_by_idempotency(db: Session, wallet_id: int, idempotency_key: str):
    return (db.query(Transaction)
            .filter(Transaction.wallet_id == wallet_id, Transaction.idempotency_key == idempotency_key)
            .first())


def create(db: Session, wallet_id: int, merchant_id: int, idempotency_key: str, amount_paise: int, cashback_paise: int = 0):
    txn = Transaction(
        wallet_id=wallet_id,
        merchant_id=merchant_id,
        idempotency_key=idempotency_key,
        amount_paise=amount_paise,
        cashback_paise=cashback_paise,
        status="PENDING"
    )
    db.add(txn)
    db.flush()
    return txn


def list_by_wallet(db: Session, wallet_id: int):
    return (db.query(Transaction)
            .filter(Transaction.wallet_id == wallet_id)
            .order_by(Transaction.id.desc()).all())


def list_by_merchant(db: Session, merchant_id: int):
    return (db.query(Transaction)
            .filter(Transaction.merchant_id == merchant_id)
            .order_by(Transaction.id.desc()).all())


def list_between(db: Session, start: datetime, end: datetime):
    return (db.query(Transaction)
            .filter(Transaction.created_at >= start, Transaction.created_at < end,
                    Transaction.status == "SUCCESS").all())


def get_month_to_date_cashback(db: Session, wallet_id: int, category: str, start: datetime, end: datetime) -> int:
    """SUM(CashbackPaise) over TRANSACTION for this wallet, category and calendar month."""
    total = (
        db.query(func.coalesce(func.sum(Transaction.cashback_paise), 0))
        .join(Merchant, Transaction.merchant_id == Merchant.id)
        .filter(
            Transaction.wallet_id == wallet_id,
            Merchant.category == category,
            Transaction.status == "SUCCESS",
            Transaction.created_at >= start,
            Transaction.created_at < end
        )
        .scalar()
    )
    return int(total)
