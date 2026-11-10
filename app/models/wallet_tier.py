from sqlalchemy import Column, String, Integer, CheckConstraint
from app.core.database import Base


class WalletTier(Base):
    __tablename__ = "wallet_tiers"

    tier = Column(String, primary_key=True)
    rate_mult_x10 = Column(Integer, nullable=False)
    cap_mult_x10 = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("rate_mult_x10 > 0", name="chk_rate_mult_pos"),
        CheckConstraint("cap_mult_x10 > 0", name="chk_cap_mult_pos"),
    )
