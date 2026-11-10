from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, Index
from app.core.database import Base
from app.core.utils import utcnow


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), index=True, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), index=True, nullable=False)
    idempotency_key = Column(String, nullable=False)
    amount_paise = Column(Integer, nullable=False)
    cashback_paise = Column(Integer, nullable=False, default=0)
    status = Column(String, default="SUCCESS")
    created_at = Column(DateTime, default=utcnow, index=True)

    __table_args__ = (
        UniqueConstraint("wallet_id", "idempotency_key", name="uq_wallet_idempotency"),
        CheckConstraint("amount_paise > 0", name="chk_amount_pos"),
        CheckConstraint("cashback_paise >= 0", name="chk_cashback_non_neg"),
        Index("ix_wallet_created_at", "wallet_id", "created_at"),
    )

    @property
    def student_id(self) -> int:
        return self.wallet_id

    @property
    def amount(self) -> float:
        return round(self.amount_paise / 100.0, 2)

    @property
    def cashback(self) -> float:
        return round(self.cashback_paise / 100.0, 2)
