from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base
from app.core.utils import utcnow


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # student | merchant | admin
    created_at = Column(DateTime, default=utcnow)
