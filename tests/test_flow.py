import os, tempfile, pytest
os.environ["FINPAY_DB"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "test.db")

from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.services.cashback_service import calculate_cashback
from app.core.errors import AppError

client = TestClient(app)


def signup_login(name, email, role):
    client.post("/auth/register", json={"name": name, "email": email, "password": "secret123", "role": role})
    token = client.post("/auth/login", json={"email": email, "password": "secret123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_calculate_cashback_lab4_edge_cases():
    """Validates all edge cases from Lab 4 Table in Part B (Algorithm Design)."""
    # 1. 10000, CANTEEN, BASIC -> 200 (₹100 @ 2% = ₹2)
    assert calculate_cashback(10000, "CANTEEN", "BASIC") == 200

    # 2. 10000, CANTEEN, PRIME -> 300 (2% * 1.5 = 3%)
    assert calculate_cashback(10000, "CANTEEN", "PRIME") == 300

    # 3. 10000, CANTEEN, PREMIUM -> 400 (2% * 2.0 = 4%)
    assert calculate_cashback(10000, "CANTEEN", "PREMIUM") == 400

    # 4. 333, CANTEEN, BASIC -> 6 (6.66 paise floored to 6)
    assert calculate_cashback(333, "CANTEEN", "BASIC") == 6

    # 5. 49, CANTEEN, BASIC -> 0 (0.98 paise floored to 0)
    assert calculate_cashback(49, "CANTEEN", "BASIC") == 0

    # 6. 50, CANTEEN, BASIC -> 1 (Exactly 1.00 paise boundary)
    assert calculate_cashback(50, "CANTEEN", "BASIC") == 1

    # 7. 10300, HOSTEL, PRIME -> 77 (0.5% * 1.5 = 0.75%; 77.25 floored to 77)
    assert calculate_cashback(10300, "HOSTEL", "PRIME") == 77

    # 8. 10000, TOPUP, any tier -> 0 (0% rate)
    assert calculate_cashback(10000, "TOPUP", "BASIC") == 0
    assert calculate_cashback(10000, "TOPUP", "PREMIUM") == 0

    # 9. amount <= 0 -> raises AppError
    with pytest.raises(AppError):
        calculate_cashback(0, "CANTEEN", "BASIC")
    with pytest.raises(AppError):
        calculate_cashback(-100, "CANTEEN", "BASIC")

    # 10. Unknown category or tier -> raises AppError
    with pytest.raises(AppError):
        calculate_cashback(1000, "GAMING", "BASIC")
    with pytest.raises(AppError):
        calculate_cashback(1000, "CANTEEN", "SUPER")


def test_full_flow():
    student = signup_login("Chaitra", "s@kle.edu", "student")
    shop = signup_login("Canteen", "m@kle.edu", "merchant")
    admin = signup_login("Admin", "a@kle.edu", "admin")

    # Register merchant under CANTEEN category
    r = client.post("/merchants", json={"business_name": "KLE Canteen", "category": "CANTEEN"}, headers=shop)
    assert r.status_code == 201
    merchant_id = r.json()["id"]

    # Topup student wallet ₹1000 (= 100000 paise)
    topup_res = client.post("/wallet/topup", json={"amount": 1000}, headers=student).json()
    assert topup_res["balance"] == 1000.0
    assert topup_res["balance_paise"] == 100000

    # Student pays ₹500 (50000 paise) -> 2% of 500 = ₹10 (1000 paise) cashback
    p1 = client.post(
        "/payments",
        json={"merchant_id": merchant_id, "amount": 500, "idempotency_key": "pay-101"},
        headers=student
    )
    assert p1.status_code == 201
    assert p1.json()["cashback"] == 10.0
    assert p1.json()["cashback_paise"] == 1000
    # Balance: 1000 - 500 + 10 = 510
    bal1 = client.get("/wallet/balance", headers=student).json()
    assert bal1["balance"] == 510.0
    assert bal1["balance_paise"] == 51000

    # Idempotency protection test: repeating identical payment with same idempotency_key must return same transaction
    p1_replay = client.post(
        "/payments",
        json={"merchant_id": merchant_id, "amount": 500, "idempotency_key": "pay-101"},
        headers=student
    )
    assert p1_replay.status_code == 201
    assert p1_replay.json()["id"] == p1.json()["id"]
    # Balance remains unchanged (no double debit)
    assert client.get("/wallet/balance", headers=student).json()["balance"] == 510.0

    # Insufficient balance test
    r_bad = client.post(
        "/payments",
        json={"merchant_id": merchant_id, "amount": 99999},
        headers=student
    )
    assert r_bad.status_code == 400
    assert client.get("/wallet/balance", headers=student).json()["balance"] == 510.0

    # Merchant receives payment
    rec = client.get("/payments/received", headers=shop)
    assert rec.status_code == 200
    assert len(rec.json()) >= 1

    # Tier update test: upgrade student to PRIME (1.5x)
    tier_res = client.post("/wallet/tier", json={"tier": "PRIME"}, headers=student)
    assert tier_res.status_code == 200
    assert tier_res.json()["tier"] == "PRIME"

    # Monthly reconciliation report (Admin only)
    now = datetime.now()
    rep = client.get(f"/reconciliation/monthly?year={now.year}&month={now.month}", headers=admin).json()
    assert rep["total_transactions"] >= 1
    assert rep["status"] == "BALANCED"
    assert rep["total_sales"] == 500.0
    assert rep["total_cashback"] == 10.0


def test_ui_served():
    r = client.get("/")
    assert r.status_code == 200 and "FinPay" in r.text
