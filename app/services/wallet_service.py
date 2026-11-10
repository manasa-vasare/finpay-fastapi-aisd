from sqlalchemy.orm import Session
from app.core.errors import AppError
from app.models import Wallet
from app.repositories import wallet_repository

MAX_TOPUP_PAISE = 5000000  # ₹50,000 in integer paise


def _wallet(db: Session, student_id: int) -> Wallet:
    wallet = wallet_repository.get_by_user(db, student_id)
    if not wallet:
        # Create automatically if missing
        wallet = wallet_repository.create_wallet(db, student_id, "BASIC")
        db.commit()
        db.refresh(wallet)
    return wallet


def get_wallet(db: Session, student_id: int) -> Wallet:
    return _wallet(db, student_id)


def get_balance(db: Session, student_id: int):
    w = _wallet(db, student_id)
    return {
        "user_id": student_id,
        "wallet_id": w.id,
        "tier": w.tier,
        "balance": w.balance,
        "balance_paise": w.balance_paise
    }


def set_tier(db: Session, student_id: int, tier: str):
    tier_upper = tier.upper()
    if tier_upper not in ("BASIC", "PRIME", "PREMIUM"):
        raise AppError("Tier must be BASIC, PRIME or PREMIUM", 400)
    w = _wallet(db, student_id)
    w.tier = tier_upper
    db.commit()
    db.refresh(w)
    return get_balance(db, student_id)


def topup(db: Session, student_id: int, amount: float = None, amount_paise: int = None):
    if amount_paise is None and amount is not None:
        amount_paise = int(round(amount * 100))
    elif amount_paise is None:
        raise AppError("Amount is required", 400)

    if amount_paise <= 0:
        raise AppError("Amount must be positive", 400)
    if amount_paise > MAX_TOPUP_PAISE:
        raise AppError(f"Maximum top-up per transaction is ₹{MAX_TOPUP_PAISE // 100}", 400)

    w = _wallet(db, student_id)
    credit(db, w, amount_paise, "TOPUP", "wallet top-up")
    db.commit()
    return get_balance(db, student_id)


def debit(db: Session, wallet: Wallet, amount_paise: int, reference: str):
    if wallet.balance_paise < amount_paise:
        raise AppError("Insufficient wallet balance", 400)
    wallet.balance_paise -= amount_paise
    wallet_repository.add_ledger(db, wallet.id, "PAYMENT", -amount_paise, reference)


def credit(db: Session, wallet: Wallet, amount_paise: int, entry_type: str, reference: str):
    wallet.balance_paise += amount_paise
    wallet_repository.add_ledger(db, wallet.id, entry_type, amount_paise, reference)


def history(db: Session, student_id: int):
    w = _wallet(db, student_id)
    return wallet_repository.ledger_for_wallet(db, w.id)


def verify_all_wallets(db: Session):
    """Reconciliation check: wallet balance_paise must equal ledger sum."""
    mismatches = []
    for w in wallet_repository.all_wallets(db):
        expected_paise = wallet_repository.ledger_sum_paise(db, w.id)
        if expected_paise != w.balance_paise:
            mismatches.append({
                "wallet_id": w.id,
                "student_id": w.student_id,
                "wallet_balance_paise": w.balance_paise,
                "ledger_total_paise": expected_paise,
                "wallet_balance": round(w.balance_paise / 100.0, 2),
                "ledger_total": round(expected_paise / 100.0, 2)
            })
    return mismatches
