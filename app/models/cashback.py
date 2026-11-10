from sqlalchemy import Column, Integer, DateTime, ForeignKey
from app.core.database import Base
from app.core.utils import utcnow


class CashbackRecord(Base):
    __tablename__ = "cashback_records"

    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), index=True, nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), unique=True, nullable=False)
    amount_paise = Column(Integer, nullable=False)
    rate_bps = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=utcnow, index=True)

    @property
    def amount(self) -> float:
        return round(self.amount_paise / 100.0, 2)

    @property
    def rate(self) -> float:
        return round(self.rate_bps / 10000.0, 4)

    @property
    def student_id(self) -> int:
        return self.wallet_id
