from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RegisterIn(BaseModel):
    name: str
    email: str
    password: str = Field(min_length=6)
    role: str = "student"  # student | merchant | admin


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class UserOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    email: str
    role: str


class TopupIn(BaseModel):
    amount: Optional[float] = Field(default=None, gt=0)
    amount_paise: Optional[int] = Field(default=None, gt=0)


class TierUpdateIn(BaseModel):
    tier: str


class BalanceOut(BaseModel):
    user_id: int
    wallet_id: Optional[int] = None
    tier: Optional[str] = "BASIC"
    balance: float
    balance_paise: Optional[int] = None


class LedgerOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    entry_type: str
    amount: float
    amount_paise: Optional[int] = None
    reference: Optional[str] = None
    created_at: datetime


class MerchantIn(BaseModel):
    business_name: str
    category: str = "CANTEEN"


class MerchantOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    user_id: int
    business_name: str
    category: str


class PaymentIn(BaseModel):
    merchant_id: int
    amount: Optional[float] = Field(default=None, gt=0)
    amount_paise: Optional[int] = Field(default=None, gt=0)
    idempotency_key: Optional[str] = None


class TransactionOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    wallet_id: Optional[int] = None
    student_id: Optional[int] = None
    merchant_id: int
    amount: float
    amount_paise: Optional[int] = None
    cashback: float
    cashback_paise: Optional[int] = None
    idempotency_key: Optional[str] = None
    status: str
    created_at: datetime


class CashbackOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    transaction_id: int
    amount: float
    amount_paise: Optional[int] = None
    rate: float
    created_at: datetime
