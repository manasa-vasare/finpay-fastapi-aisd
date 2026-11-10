from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    business_name = Column(String, nullable=False)
    category = Column(String, ForeignKey("cashback_rules.category"), nullable=False, default="CANTEEN")
