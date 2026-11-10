from datetime import datetime
from sqlalchemy.orm import Session
from app.models import CashbackRecord, CashbackRule, WalletTier


def get_rule(db: Session, category: str):
    return db.query(CashbackRule).filter(CashbackRule.category == category).first()


def list_rules(db: Session):
    return db.query(CashbackRule).all()


def get_tier(db: Session, tier: str):
    return db.query(WalletTier).filter(WalletTier.tier == tier).first()


def list_tiers(db: Session):
    return db.query(WalletTier).all()


def create(db: Session, wallet_id: int, transaction_id: int, amount_paise: int, rate_bps: int):
    rec = CashbackRecord(
        wallet_id=wallet_id,
        transaction_id=transaction_id,
        amount_paise=amount_paise,
        rate_bps=rate_bps
    )
    db.add(rec)
    db.flush()
    return rec


def list_by_wallet(db: Session, wallet_id: int):
    return (db.query(CashbackRecord).filter(CashbackRecord.wallet_id == wallet_id)
            .order_by(CashbackRecord.id.desc()).all())


def list_between(db: Session, start: datetime, end: datetime):
    return (db.query(CashbackRecord)
            .filter(CashbackRecord.created_at >= start, CashbackRecord.created_at < end).all())
