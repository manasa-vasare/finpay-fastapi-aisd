from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
import os

from app.core.database import Base, engine, SessionLocal
from app.core.errors import AppError
from app.core.security import hash_password
import app.models  # noqa: F401  (registers tables)
from app.models import User, Wallet, WalletLedger, Merchant
from app.routers import (auth_router, wallet_router, merchant_router,
                         payment_router, cashback_router, reconciliation_router)
from app.services.cashback_service import seed_rules_and_tiers

Base.metadata.create_all(bind=engine)


def seed_demo_accounts(db):
    """Seed ready-to-use demo accounts if missing."""
    demos = [
        ("student@campus.edu", "Alex Student", "password123", "student"),
        ("canteen@campus.edu", "Campus Canteen", "password123", "merchant"),
        ("admin@campus.edu", "System Administrator", "password123", "admin"),
    ]
    for email, name, pwd, role in demos:
        u = db.query(User).filter(User.email == email).first()
        if not u:
            u = User(name=name, email=email, password_hash=hash_password(pwd), role=role)
            db.add(u)
            db.flush()
            if role == "student":
                w = db.query(Wallet).filter(Wallet.student_id == u.id).first()
                if not w:
                    w = Wallet(student_id=u.id, tier="BASIC", balance_paise=100000)
                    db.add(w)
                    db.flush()
                    db.add(WalletLedger(wallet_id=w.id, entry_type="TOPUP", amount_paise=100000, reference="Demo Initial Deposit"))
            elif role == "merchant":
                m = db.query(Merchant).filter(Merchant.user_id == u.id).first()
                if not m:
                    db.add(Merchant(user_id=u.id, business_name="Campus Canteen", category="CANTEEN"))
    db.commit()


# Seed lookup tables and demo accounts on startup
try:
    with SessionLocal() as db:
        seed_rules_and_tiers(db)
        seed_demo_accounts(db)
except Exception:
    pass

app = FastAPI(title="FinPay - Campus Digital Wallet & Payments (Lab 4 Detailed Design)")


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


for r in (auth_router, wallet_router, merchant_router, payment_router, cashback_router, reconciliation_router):
    app.include_router(r.router)


@app.get("/", include_in_schema=False)
def ui():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))


@app.get("/health", tags=["Health"])
def health():
    return {
        "app": "FinPay",
        "architecture": "Layered Architecture (Router -> Service -> Repository -> Model -> Database)",
        "lab": "Laboratory 4 – AI-Assisted Detailed Design (3NF Schema, Integer Paise, Basis Points, Idempotency)",
        "docs": "/docs"
    }
