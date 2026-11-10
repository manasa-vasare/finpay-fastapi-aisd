# 💳 FinPay — Institutional Campus Payments, Digital Wallet & Automated Cashback

FinPay is a closed-loop digital campus payment and wallet platform built with **Python, FastAPI, SQLAlchemy, and SQLite**. 

Designed specifically for colleges, universities, and institutional campuses, FinPay allows **students** to store money in a digital wallet, pay **campus merchants** (such as canteens, stationery stores, transport, and hostels), earn **instant cashback rewards**, and empowers **administrators** to conduct automated **monthly financial reconciliations** and ledger audits.

---

## 📖 What is FinPay? (In Plain English)

Imagine a college campus where thousands of daily transactions happen: students buying meals at the canteen, printing lab manuals at the stationery shop, paying for hostel mess, or booking campus shuttle rides. 

Handling physical cash causes change shortages, lost coins, and slow lines. External payment apps frequently suffer from bank server downtime, slow OTPs, and zero student benefits. For college administrations, reconciling whether vendors received accurate payments requires days of manual paper receipts.

**FinPay solves this completely:**
* **Zero-Downtime Campus Wallet:** Students deposit funds into their campus wallet and pay campus stores in seconds.
* **Instant Automatic Cashback:** Every eligible purchase awards instant cashback credited directly back to the student's wallet balance.
* **100% Exact Math (No Money Glitches):** All currency is calculated down to the exact **integer paisa** (₹1 = 100 paise) using integer arithmetic. No floating-point rounding bugs.
* **Duplicate-Payment Protection (Idempotency):** Double-clicking or network hiccups will never charge a student twice.
* **Automated Monthly Accounting:** Campus administrators generate monthly audit reports with one click, showing total campus sales, cashback distributed, merchant payouts, and automated balance-integrity verification (`BALANCED`).

---

## 👥 Three Specialized Roles

| Role | What They Can Do |
| :--- | :--- |
| **🎓 Student** | • Checks live digital wallet balance and integer paise.<br>• Upgrades membership tier (`BASIC`, `PRIME`, `PREMIUM`) to earn higher multipliers.<br>• Tops up wallet balance.<br>• Makes one-click payments to campus merchants with instant cashback.<br>• Views complete transaction activity and double-entry wallet ledger history. |
| **🏪 Merchant** | • Registers store profile under standard categories (`CANTEEN`, `STATIONERY`, `TRANSPORT`, `HOSTEL`, `ONLINE`).<br>• Accepts payments directly from students.<br>• Tracks aggregate sales volume and real-time customer transaction logs. |
| **⚖️ Administrator** | • Runs monthly reconciliation reports for any year and month.<br>• Audits campus-wide gross volume, total cashback given, and net settlement owed to each merchant.<br>• Runs mathematical double-entry consistency checks across all student wallets (`STATUS: BALANCED`). |

---

## 🎨 User Experience & Design

FinPay features a **frosted-glass (glassmorphism)** multi-page interface:
* **Glassmorphic Aesthetics:** Frosted translucent cards (`backdrop-filter: blur(18px)`), ambient light orbs, and crisp light borders.
* **Role-Specific Sidebars:** Each role gets its own tailored sidebar with distinct pages and tools.
* **Dedicated Multi-Page Views:** No cluttered, endlessly scrolling single page. Each feature (Balance, Deposit, Pay, Rules, Activity, Ledger) has its own focused page view.
* **Instant 1-Click Demo Login:** The login screen includes a sidebar featuring pre-seeded demo accounts (Student preloaded with ₹1,000, Merchant, and Administrator) with direct one-click sign-in buttons.
* **Professional Standards:** 100% free of casual emojis, featuring clean SVG iconography and tabular figure alignment for financial numbers.

---

## 📐 Business Rules & Tier System (Lab 4 Detailed Design)

### 1. Student Tiers (`WALLET_TIER`)
Each student wallet is classified under a tier that scales both their cashback rate and calendar monthly cap:

| Tier | Rate Multiplier | Monthly Cap Multiplier | Description |
| :---: | :---: | :---: | :--- |
| **`BASIC`** | **1.0x** (`RateMultX10 = 10`) | **1.0x** (`CapMultX10 = 10`) | Standard student enrollment (Default). |
| **`PRIME`** | **1.5x** (`RateMultX10 = 15`) | **1.5x** (`CapMultX10 = 15`) | **50% higher** cashback rate and monthly cap. |
| **`PREMIUM`** | **2.0x** (`RateMultX10 = 20`) | **2.0x** (`CapMultX10 = 20`) | **Double (2x)** cashback rate and monthly cap. |

---

### 2. Category Cashback Rules (`CASHBACK_RULE`)
Every merchant belongs to an approved campus category with specific base rates in **Basis Points (Bps)** ($100\text{ Bps} = 1.0\%$) and monthly caps:

| Category | Base Rate (Bps) | Base Rate (%) | Base Monthly Cap |
| :--- | :---: | :---: | :---: |
| **`CANTEEN`** | 200 Bps | **2.0%** | ₹50.00 (5,000 paise) |
| **`STATIONERY`** | 100 Bps | **1.0%** | ₹20.00 (2,000 paise) |
| **`TRANSPORT`** | 300 Bps | **3.0%** | ₹100.00 (10,000 paise) |
| **`HOSTEL`** | 50 Bps | **0.5%** | ₹200.00 (20,000 paise) |
| **`ONLINE`** | 100 Bps | **1.0%** | ₹30.00 (3,000 paise) |
| **`TOPUP`** | 0 Bps | **0.0%** | ₹0.00 (0 paise) |

---

### 3. The Cashback Algorithm (`calculate_cashback`)
Cashback is calculated via a **pure mathematical function** using 64-bit integer floor division:

$$\text{Raw Cashback (paise)} = \left\lfloor \frac{\text{AmountPaise} \times \text{BaseRateBps} \times \text{RateMultX10}}{100{,}000} \right\rfloor$$

$$\text{Effective Monthly Cap} = \left\lfloor \frac{\text{BaseMonthlyCapPaise} \times \text{CapMultX10}}{10} \right\rfloor$$

$$\text{Awarded Cashback} = \min\Big(\text{Raw Cashback},\; \max\big(0,\; \text{Effective Monthly Cap} - \text{Month-to-Date Earned}\big)\Big)$$

---

## 🏗️ System Architecture

FinPay strictly adheres to **Layered Architecture**:

```
Browser / REST API Client
        ↓
Router Layer        (FastAPI routers: checks JWT role, validates input)
        ↓
Service Layer       (Business logic: atomic payment, pure cashback algorithm, reconciliation)
        ↓
Repository Layer    (Data access: queries & persists models, no business rules)
        ↓
Model Layer         (SQLAlchemy 3NF database schema & constraints)
        ↓
Database            (SQLite: finpay.db)
```

---

## 🗄️ Relational Database Schema (3NF)

```
STUDENT ────── (1 : 0..1) ────── WALLET ────── (1 : N) ────── TRANSACTION
                                   │                              │
                                   │ (N : 1)                      │ (N : 1)
                                   ▼                              ▼
                              WALLET_TIER                      MERCHANT
                       (BASIC, PRIME, PREMIUM)                    │
                                                                  │ (N : 1)
                                                                  ▼
                                                            CASHBACK_RULE
                                                    (CANTEEN, HOSTEL, etc.)
```

* **`STUDENT` / `User`:** Authentication credentials (JWT, password hash, role).
* **`WALLET`:** `WalletID`, `StudentID` (UNIQUE), `Tier` (FK), `BalancePaise` (CHECK $\ge$ 0).
* **`WALLET_TIER`:** `Tier` (PK), `RateMultX10`, `CapMultX10`.
* **`CASHBACK_RULE`:** `Category` (PK), `BaseRateBps`, `BaseMonthlyCapPaise`.
* **`MERCHANT`:** `MerchantID`, `UserID`, `BusinessName`, `Category` (FK).
* **`TRANSACTION`:** `TransactionID`, `WalletID` (FK), `MerchantID` (FK), `IdempotencyKey`, `AmountPaise`, `CashbackPaise`, `CreatedAt`, with `UNIQUE(WalletID, IdempotencyKey)`.
* **`WalletLedger`:** Double-entry audit entries (`TOPUP`, `PAYMENT`, `CASHBACK`).

---

## 🚀 How to Run the Project

### Prerequisites
* **Python 3.10+** (Tested on Python 3.10, 3.11, 3.12, 3.13)
* Git

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/manasa-vasare/finpay-fastapi-aisd.git
cd finpay-fastapi-aisd
```

---

### Step 2: Install Dependencies
Create a virtual environment (optional but recommended) and install dependencies:
```bash
pip install -r requirements.txt
```

---

### Step 3: Run the Application
Start the server using Uvicorn:
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

### Step 4: Open in Your Browser
* **Web Application UI:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Interactive API Documentation (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Alternative API Docs (ReDoc):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **Health Check Endpoint:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🔑 Pre-Configured Demo Accounts (1-Click Login)

The application automatically seeds ready-to-test demo accounts on startup. You can click the **"Sign In as..."** buttons on the login screen or enter the credentials manually:

| Account Type | Email | Password | Pre-loaded State |
| :--- | :--- | :--- | :--- |
| **Student** | `student@campus.edu` | `password123` | Pre-funded with **₹1,000.00** ($100{,}000\text{ paise}$) on Basic Tier. |
| **Merchant** | `canteen@campus.edu` | `password123` | Configured as **Campus Canteen** under `CANTEEN` category. |
| **Administrator** | `admin@campus.edu` | `password123` | Access to monthly reconciliation statements & ledger audit. |

---

## 🧪 Running Automated Tests

Run the automated test suite using `pytest`:

```bash
pytest
```

### Verified Test Cases Include:
1. `(10000 paise, CANTEEN, BASIC)` $\rightarrow$ **200 paise** (₹100 @ 2% = ₹2.00)
2. `(10000 paise, CANTEEN, PRIME)` $\rightarrow$ **300 paise** (2% $\times$ 1.5 = 3%)
3. `(10000 paise, CANTEEN, PREMIUM)` $\rightarrow$ **400 paise** (2% $\times$ 2.0 = 4%)
4. `(333 paise, CANTEEN, BASIC)` $\rightarrow$ **6 paise** (6.66 floored to 6)
5. `(49 paise, CANTEEN, BASIC)` $\rightarrow$ **0 paise** (0.98 floored to 0; below 1-paisa boundary)
6. `(50 paise, CANTEEN, BASIC)` $\rightarrow$ **1 paisa** (Exact 1.00 paisa minimum reward boundary)
7. `(10300 paise, HOSTEL, PRIME)` $\rightarrow$ **77 paise** (0.5% $\times$ 1.5 = 0.75%; 77.25 floored to 77)
8. `(10000 paise, TOPUP, any tier)` $\rightarrow$ **0 paise** (0% rate)
9. Idempotency replay check: Duplicate request with identical `IdempotencyKey` returns existing transaction without double-charging.
10. Insufficient balance rejection.
11. Double-entry audit balance verification (`STATUS: BALANCED`).

---

## 🛠️ Tech Stack Summary

* **Backend:** Python 3, FastAPI (ASGI)
* **Web Server:** Uvicorn
* **Database & ORM:** SQLite, SQLAlchemy
* **Authentication:** PyJWT (HMAC-SHA256) + PBKDF2/SHA-256 password hashing
* **Testing:** Pytest, HTTPX TestClient
* **Frontend:** Vanilla JavaScript (ES6+), HTML5, Glassmorphism CSS (Zero framework dependencies, no `npm`/Node.js build step needed)

---

## 📜 License & Academic Attribution
Developed as an implementation of **Laboratory 4 — AI-Assisted Detailed Design (Data, Algorithm, and Security Design)** for the Campus FinPay ecosystem.
