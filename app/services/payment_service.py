import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.errors import AppError
from app.core.utils import utcnow
from app.repositories import transaction_repository, cashback_repository
from app.services import wallet_service, merchant_service, cashback_service


def pay(db: Session, student, merchant_id: int, amount: float = None, amount_paise: int = None, idempotency_key: str = None):
    # Normalize amount to integer paise
    if amount_paise is None and amount is not None:
        amount_paise = int(round(amount * 100))
    elif amount_paise is None:
        raise AppError("Payment amount is required", 400)

    if amount_paise <= 0:
        raise AppError("Amount must be positive", 400)

    # Resolve or create wallet for student
    wallet = wallet_service.get_wallet(db, student.id)

    # Generate or enforce idempotency key
    if not idempotency_key:
        idempotency_key = str(uuid.uuid4())

    # Check for duplicate idempotency key (idempotent replay)
    existing = transaction_repository.get_by_idempotency(db, wallet.id, idempotency_key)
    if existing:
        return existing

    merchant = merchant_service.get_or_404(db, merchant_id)

    # 1. Calculate raw cashback using Lab 4 pure function
    raw_cashback_paise = cashback_service.calculate_cashback(
        amount_paise=amount_paise,
        category=merchant.category,
        tier=wallet.tier
    )

    # 2. Apply monthly cap for (wallet, category, calendar month)
    now = utcnow()
    start_of_month = datetime(now.year, now.month, 1)
    end_of_month = datetime(now.year + 1, 1, 1) if now.month == 12 else datetime(now.year, now.month + 1, 1)

    earned_month_to_date = transaction_repository.get_month_to_date_cashback(
        db, wallet.id, merchant.category, start_of_month, end_of_month
    )
    monthly_cap_paise = cashback_service.get_monthly_cap_paise(merchant.category, wallet.tier)
    remaining_cap = max(0, monthly_cap_paise - earned_month_to_date)
    awarded_cashback_paise = min(raw_cashback_paise, remaining_cap)

    # 3. Atomic execution
    try:
        # Check balance and debit
        wallet_service.debit(db, wallet, amount_paise, f"Payment to {merchant.business_name}")

        # Credit awarded cashback if any
        if awarded_cashback_paise > 0:
            wallet_service.credit(db, wallet, awarded_cashback_paise, "CASHBACK", f"Cashback for txn to {merchant.business_name}")

        # Insert transaction
        txn = transaction_repository.create(
            db,
            wallet_id=wallet.id,
            merchant_id=merchant.id,
            idempotency_key=idempotency_key,
            amount_paise=amount_paise,
            cashback_paise=awarded_cashback_paise
        )
        txn.status = "SUCCESS"

        if awarded_cashback_paise > 0:
            cashback_repository.create(
                db,
                wallet_id=wallet.id,
                transaction_id=txn.id,
                amount_paise=awarded_cashback_paise,
                rate_bps=cashback_service.RATE_TABLE[merchant.category].base_rate_bps
            )

        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(txn)
    return txn


def student_history(db: Session, student_id: int):
    wallet = wallet_service.get_wallet(db, student_id)
    return transaction_repository.list_by_wallet(db, wallet.id)


def merchant_history(db: Session, user):
    merchant = merchant_service.my_profile(db, user)
    return transaction_repository.list_by_merchant(db, merchant.id)
