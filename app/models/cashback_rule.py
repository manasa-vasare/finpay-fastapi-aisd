from sqlalchemy import Column, String, Integer, CheckConstraint
from app.core.database import Base


class CashbackRule(Base):
    __tablename__ = "cashback_rules"

    category = Column(String, primary_key=True)
    base_rate_bps = Column(Integer, nullable=False)
    base_monthly_cap_paise = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("base_rate_bps >= 0", name="chk_base_rate_non_neg"),
        CheckConstraint("base_monthly_cap_paise >= 0", name="chk_monthly_cap_non_neg"),
    )
