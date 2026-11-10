from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Wallet, WalletLedger


def create_wallet(db: Session, student_id: int, tier: str = "BASIC"):
    wallet = Wallet(student_id=student_id, tier=tier, balance_paise=0)
    db.add(wallet)
    db.flush()
    return wallet


def get_by_user(db: Session, student_id: int):
    return db.query(Wallet).filter(Wallet.student_id == student_id).first()


def get(db: Session, wallet_id: int):
    return db.query(Wallet).filter(Wallet.id == wallet_id).first()


def all_wallets(db: Session):
    return db.query(Wallet).all()


def add_ledger(db: Session, wallet_id: int, entry_type: str, amount_paise: int, reference: str = None):
    entry = WalletLedger(wallet_id=wallet_id, entry_type=entry_type, amount_paise=amount_paise, reference=reference)
    db.add(entry)
    db.flush()
    return entry


def ledger_for_wallet(db: Session, wallet_id: int):
    return (db.query(WalletLedger).filter(WalletLedger.wallet_id == wallet_id)
            .order_by(WalletLedger.id.desc()).all())


def ledger_sum_paise(db: Session, wallet_id: int) -> int:
    total = db.query(func.coalesce(func.sum(WalletLedger.amount_paise), 0)).filter(
        WalletLedger.wallet_id == wallet_id).scalar()
    return int(total)
