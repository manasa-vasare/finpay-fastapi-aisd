from datetime import datetime
from sqlalchemy.orm import Session
from app.core.errors import AppError
from app.repositories import transaction_repository, merchant_repository
from app.services import wallet_service


def monthly_report(db: Session, year: int, month: int):
    if not 1 <= month <= 12:
        raise AppError("Month must be between 1 and 12", 400)
    start = datetime(year, month, 1)
    end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

    txns = transaction_repository.list_between(db, start, end)

    per_merchant = {}
    for t in txns:
        m = per_merchant.setdefault(t.merchant_id, {
            "merchant_id": t.merchant_id,
            "transactions": 0,
            "gross_sales_paise": 0,
            "cashback_given_paise": 0
        })
        m["transactions"] += 1
        m["gross_sales_paise"] += t.amount_paise
        m["cashback_given_paise"] += t.cashback_paise

    for m in per_merchant.values():
        merchant = merchant_repository.get(db, m["merchant_id"])
        m["business_name"] = merchant.business_name if merchant else "Unknown Merchant"
        m["category"] = merchant.category if merchant else "CANTEEN"
        m["settlement_due_paise"] = m["gross_sales_paise"]
        m["gross_sales"] = round(m["gross_sales_paise"] / 100.0, 2)
        m["cashback_given"] = round(m["cashback_given_paise"] / 100.0, 2)
        m["settlement_due"] = round(m["settlement_due_paise"] / 100.0, 2)

    total_sales_paise = sum(t.amount_paise for t in txns)
    total_cashback_paise = sum(t.cashback_paise for t in txns)
    mismatches = wallet_service.verify_all_wallets(db)

    return {
        "period": f"{year}-{month:02d}",
        "total_transactions": len(txns),
        "total_sales_paise": total_sales_paise,
        "total_cashback_paise": total_cashback_paise,
        "total_sales": round(total_sales_paise / 100.0, 2),
        "total_cashback": round(total_cashback_paise / 100.0, 2),
        "merchants": list(per_merchant.values()),
        "wallet_mismatches": mismatches,
        "status": "BALANCED" if not mismatches else "MISMATCH_FOUND",
    }
