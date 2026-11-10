from dataclasses import dataclass
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.core.errors import AppError
from app.models import CashbackRule, WalletTier
from app.repositories import cashback_repository

# Constants defined in Lab 4 DDR
BPS_SCALE = 10000     # 1 basis point = 0.01%
MULT_SCALE = 10        # multipliers stored x10: 1.0->10, 1.5->15, 2.0->20
DIVISOR = BPS_SCALE * MULT_SCALE  # 100000 (64-bit integer division)


@dataclass(frozen=True)
class RateRule:
    category: str
    base_rate_bps: int
    base_monthly_cap_paise: int


@dataclass(frozen=True)
class TierRule:
    tier: str
    rate_mult_x10: int
    cap_mult_x10: int


# Default in-memory tables for pure function evaluation
RATE_TABLE: Dict[str, RateRule] = {
    "CANTEEN": RateRule("CANTEEN", 200, 5000),      # 2.0%, ₹50 cap
    "STATIONERY": RateRule("STATIONERY", 100, 2000), # 1.0%, ₹20 cap
    "TRANSPORT": RateRule("TRANSPORT", 300, 10000),  # 3.0%, ₹100 cap
    "HOSTEL": RateRule("HOSTEL", 50, 20000),         # 0.5%, ₹200 cap
    "ONLINE": RateRule("ONLINE", 100, 3000),         # 1.0%, ₹30 cap
    "TOPUP": RateRule("TOPUP", 0, 0),                # 0.0%, ₹0 cap
}

TIER_TABLE: Dict[str, TierRule] = {
    "BASIC": TierRule("BASIC", 10, 10),      # 1.0x rate, 1.0x cap
    "PRIME": TierRule("PRIME", 15, 15),      # 1.5x rate, 1.5x cap
    "PREMIUM": TierRule("PREMIUM", 20, 20),  # 2.0x rate, 2.0x cap
}


def seed_rules_and_tiers(db: Session):
    """Seed default 3NF lookup tables if not already present."""
    for tier_key, t in TIER_TABLE.items():
        if not db.query(WalletTier).filter(WalletTier.tier == tier_key).first():
            db.add(WalletTier(tier=t.tier, rate_mult_x10=t.rate_mult_x10, cap_mult_x10=t.cap_mult_x10))

    for cat_key, r in RATE_TABLE.items():
        if not db.query(CashbackRule).filter(CashbackRule.category == cat_key).first():
            db.add(CashbackRule(category=r.category, base_rate_bps=r.base_rate_bps, base_monthly_cap_paise=r.base_monthly_cap_paise))

    db.commit()


def calculate_cashback(amount_paise: int, category: str, tier: str) -> int:
    """
    Lab 4 critical function: Pure function, integer arithmetic only, ONE floor at the end.
    Returns the raw cashback in paise for one payment, before the monthly cap.
    """
    # Preconditions
    if not isinstance(amount_paise, int) or amount_paise <= 0:
        raise AppError("InvalidAmount: amount_paise must be positive integer", 400)

    cat_upper = str(category).upper()
    if cat_upper not in RATE_TABLE:
        raise AppError(f"UnknownCategory: '{category}' is not valid", 400)

    tier_upper = str(tier).upper()
    if tier_upper not in TIER_TABLE:
        raise AppError(f"UnknownTier: '{tier}' is not valid", 400)

    # In-memory lookup: no DB access
    rate_bps = RATE_TABLE[cat_upper].base_rate_bps
    mult_x10 = TIER_TABLE[tier_upper].rate_mult_x10

    if rate_bps == 0:
        return 0

    # Single integer floor division
    raw_paise = (amount_paise * rate_bps * mult_x10) // DIVISOR
    return raw_paise


def get_monthly_cap_paise(category: str, tier: str) -> int:
    """Calculates effective monthly cap in paise: (BaseMonthlyCapPaise * CapMultX10) // 10"""
    cat_upper = str(category).upper()
    tier_upper = str(tier).upper()
    if cat_upper not in RATE_TABLE or tier_upper not in TIER_TABLE:
        return 0
    base_cap = RATE_TABLE[cat_upper].base_monthly_cap_paise
    cap_mult = TIER_TABLE[tier_upper].cap_mult_x10
    return (base_cap * cap_mult) // MULT_SCALE


def rules():
    """Return categorized rules and tiers for display."""
    return {
        "categories": [
            {
                "category": r.category,
                "base_rate_percent": round(r.base_rate_bps / 100.0, 2),
                "base_rate_bps": r.base_rate_bps,
                "base_monthly_cap_paise": r.base_monthly_cap_paise,
                "base_monthly_cap_rupees": round(r.base_monthly_cap_paise / 100.0, 2),
            }
            for r in RATE_TABLE.values()
        ],
        "tiers": [
            {
                "tier": t.tier,
                "rate_multiplier": round(t.rate_mult_x10 / 10.0, 1),
                "cap_multiplier": round(t.cap_mult_x10 / 10.0, 1),
            }
            for t in TIER_TABLE.values()
        ],
        # Backward compatibility for legacy UI calls
        "rate_percent": 2.0,
        "min_payment": 0.5,
        "max_cashback_per_payment": 50.0,
    }


def history(db: Session, wallet_id: int):
    return cashback_repository.list_by_wallet(db, wallet_id)
