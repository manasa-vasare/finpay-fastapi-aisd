from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from app.core.database import Base
from app.core.utils import utcnow


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    tier = Column(String, ForeignKey("wallet_tiers.tier"), nullable=False, default="BASIC")
    balance_paise = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint("balance_paise >= 0", name="chk_wallet_balance_non_neg"),
    )

    @property
    def user_id(self) -> int:
        return self.student_id

    @property
    def balance(self) -> float:
        return round(self.balance_paise / 100.0, 2)


class WalletLedger(Base):
    __tablename__ = "wallet_ledger"

    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), index=True, nullable=False)
    entry_type = Column(String, nullable=False)  # TOPUP, PAYMENT, CASHBACK
    amount_paise = Column(Integer, nullable=False)  # signed integer paise
    reference = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    @property
    def amount(self) -> float:
        return round(self.amount_paise / 100.0, 2)
