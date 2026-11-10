# FinPay — Campus Digital Wallet, Payments & Automatic Cashback

FinPay is a closed-loop digital campus wallet platform built with **Python, FastAPI, SQLAlchemy, and SQLite**. 

Designed specifically for universities and colleges, FinPay allows **students** to store money in a digital wallet, pay **campus merchants** (such as canteens, stationery stores, hostels, and transport), earn **instant cashback rewards**, and empowers **administrators** to conduct automated **monthly financial reconciliations** and ledger audits.

---

## Table of Contents
1. [What is FinPay? (In Plain English)](#what-is-finpay-in-plain-english)
2. [Key Features by Role](#key-features-by-role)
3. [User Experience & Design](#user-experience--design)
4. [How the System Works](#how-the-system-works)
5. [Cashback Rules & Student Tiers](#cashback-rules--student-tiers)
6. [Step-by-Step Setup & How to Run](#step-by-step-setup--how-to-run)
7. [Pre-Configured Demo Accounts](#pre-configured-demo-accounts)
8. [System Architecture & Data Design](#system-architecture--data-design)
9. [Running Automated Tests](#running-automated-tests)
10. [Technology Stack](#technology-stack)

---

## What is FinPay? (In Plain English)

Imagine a college campus where thousands of daily transactions happen: students buying meals at the canteen, printing notes at the stationery shop, paying for hostel laundry, or booking campus shuttle rides. 

Handling cash causes change shortages and lost coins. Generic UPI apps frequently suffer from bank server downtime, slow OTPs, and zero rewards. For university administrators, verifying whether campus vendors received accurate payments requires days of manual paper reconciliation.

**FinPay solves this completely:**
- **Zero Downtime Closed-Loop Wallet:** Students top up their account and pay on-campus merchants instantly.
- **Automated Cashback:** Every purchase earns automatic cashback credited immediately back to the student's wallet balance.
- **No Money Rounding Bugs:** All currency is tracked down to the exact **integer paisa** (no floating-point rounding errors).
- **One-Click Settlement:** At the end of every month, campus administrators generate an audit report showing total sales, cashback given, net payouts owed to merchants, and automated balance-integrity verification.

---

## Key Features by Role

### 1. Student Portal
* **Automated Provisioning:** Signing up automatically initializes an individual digital wallet.
* **Wallet Top-Up:** Deposit funds with preset amount shortcuts (+₹200, +₹500, +₹1,000, +₹2,000).
* **Merchant Payments:** Choose any registered merchant, input payment amount, and authorize transfer.
* **Instant Rewards:** Cashback is calculated and credited in the same millisecond the payment succeeds.
* **Membership Tiers:** Students can upgrade tiers (`BASIC`, `PRIME`, `PREMIUM`) to multiply their cashback rate and monthly caps up to **2.0x**.
* **Audit Trail:** Dedicated payment history table and double-entry accounting ledger showing every debit, credit, and reference note.

### 2. Merchant Portal
* **Store Onboarding:** Register a store profile under approved campus categories (`CANTEEN`, `STATIONERY`, `TRANSPORT`, `HOSTEL`, `ONLINE`).
* **Live Inflow Counter:** Track aggregate gross sales volume and total customer count.
* **Inbound Payment Ledger:** Live log of customer receipts with student wallet IDs, amounts, and idempotency tracking.

### 3. Administrator Portal
* **Monthly Financial Reconciliation:** Select any year and month to audit all completed transactions across campus.
* **Merchant Settlement Schedule:** Clear schedule detailing gross sales, cashback absorbed, and net payout payable to each campus vendor.
* **Ledger Consistency Audit:** Verifies the mathematical integrity of every student wallet:
  $$\text{Wallet Balance} \stackrel{?}{=} \sum (\text{Ledger Entries})$$
  * If balanced: Flags `STATUS: BALANCED`.
  * If any discrepancy exists: Flags `AUDIT: MISMATCH DETECTED` with the exact variance.

---

## User Experience & Design

FinPay features a **Multi-Page Frosted Glass (Glassmorphism)** dashboard:
* **Dedicated Multi-Page Navigation:** Separate, focused screens for Overview, Deposits, Payments, Cashback Schedules, and Ledger Logs—no cluttered, long-scrolling stacks.
* **Role-Specific Sidebars:** When logged in, the navigation sidebar automatically adapts to your role (Student tools for students, Store tools for merchants, Audit tools for admins).
* **Instant Demo Sidebar:** The authentication screen includes a quick-access side panel with 1-click login buttons for Student, Merchant, and Administrator profiles.
* **Zero Emojis & Professional Fintech Styling:** High-contrast slate typography (`#0f172a`), clean SVG icons, and tabular numeral alignment for monetary precision.

---

## How the System Works

### 1. The Payment Engine (Atomic Unit of Work)
When a student pays a merchant:
1. **Idempotency Protection:** The client attaches a unique `IdempotencyKey`. If a student double-clicks or the network retries, the server recognizes the key and **will not charge the wallet twice**.
2. **Balance Validation:** The system verifies `wallet.balance_paise >= amount_paise`. If funds are insufficient, the transaction aborts with an HTTP 400 error.
3. **Pure Cashback Calculation:** The cashback engine evaluates the category rate and student tier multiplier in memory.
4. **Monthly Cap Check:** The system queries month-to-date cashback earned by that student in that category for the current calendar month and caps the reward.
5. **Atomic Commit:**
   - Debit student wallet: `balance -= amount`
   - Credit student wallet: `balance += cashback`
   - Log `PAYMENT` ledger row
   - Log `CASHBACK` ledger row
   - Record `TRANSACTION` as `SUCCESS`
   - *Everything commits together in one atomic database operation. If any step fails, the entire transaction rolls back completely.*

---

## Cashback Rules & Student Tiers

### 1. Category Base Rates & Monthly Caps (3NF)

| Category | Base Rate (Basis Points) | Base Rate (%) | Base Monthly Cap (Paise) | Base Monthly Cap (₹) |
| :--- | :---: | :---: | :---: | :---: |
| **CANTEEN** | 200 Bps | 2.0% | 5,000 paise | ₹50.00 / month |
| **STATIONERY** | 100 Bps | 1.0% | 2,000 paise | ₹20.00 / month |
| **TRANSPORT** | 300 Bps | 3.0% | 10,000 paise | ₹100.00 / month |
| **HOSTEL** | 50 Bps | 0.5% | 20,000 paise | ₹200.00 / month |
| **ONLINE** | 100 Bps | 1.0% | 3,000 paise | ₹30.00 / month |
| **TOPUP** | 0 Bps | 0.0% | 0 paise | ₹0.00 |

### 2. Membership Tiers & Multipliers

| Tier | Rate Multiplier | Cap Multiplier | Effect on Earnings |
| :--- | :---: | :---: | :--- |
| **`BASIC`** | **1.0x** (`10`) | **1.0x** (`10`) | Standard category base rate and standard monthly cap. |
| **`PRIME`** | **1.5x** (`15`) | **1.5x** (`15`) | **50% higher** cashback rate and monthly cap. |
| **`PREMIUM`** | **2.0x** (`20`) | **2.0x** (`20`) | **Double (2x)** cashback rate and monthly cap. |

#### Formula:
$$\text{Raw Cashback (paise)} = \left\lfloor \frac{\text{AmountPaise} \times \text{BaseRateBps} \times \text{RateMultX10}}{100{,}000} \right\rfloor$$
$$\text{Effective Monthly Cap (paise)} = \left\lfloor \frac{\text{BaseMonthlyCapPaise} \times \text{CapMultX10}}{10} \right\rfloor$$

---

## Step-by-Step Setup & How to Run

### 1. Prerequisites
* **Python 3.10** or newer installed on your machine.
* Standard terminal (PowerShell, Command Prompt, macOS Terminal, or Linux Bash).

### 2. Installation
Open your terminal in the project directory (`FINPAY-main`):

```bash
# Optional: create a virtual environment
python -m venv venv

# Activate on Windows:
venv\Scripts\activate
# Or activate on macOS/Linux:
source venv/bin/activate

# Install dependencies:
pip install -r requirements.txt
```

### 3. Start the Server
Run the application using Uvicorn:

```bash
python -m uvicorn app.main:app --reload
```

To run on a specific port (for example, if 8000 is occupied):
```bash
python -m uvicorn app.main:app --reload --port 8001
```

### 4. Access the Application
Once the server starts, open your web browser:
* **Web Application:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Interactive Swagger API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **System Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

The database file `finpay.db` is automatically created and seeded with lookup tables and demo accounts on first launch.

---

## Pre-Configured Demo Accounts

For fast testing and demonstrations, the application pre-seeds ready-to-use accounts. You can click **"Sign In as..."** on the login screen side panel for instant 1-click access:

| Role | Email | Password | Pre-configured State |
| :--- | :--- | :--- | :--- |
| **Student** | `student@campus.edu` | `password123` | Pre-loaded with **₹1,000.00** balance on the `BASIC` Tier. |
| **Merchant** | `canteen@campus.edu` | `password123` | Store profile: **Campus Canteen** under `CANTEEN` category. |
| **Admin** | `admin@campus.edu` | `password123` | Institutional Auditor with access to monthly statements. |

*You can also click **"Register New Account"** on the login screen to create custom accounts.*

---

## System Architecture & Data Design

### 1. Layered Architecture
Requests flow downward with strict boundary separation:

```
Browser / Client (Vanilla JS + HTML5 + CSS3)
        │
        ▼
Routers (FastAPI API Layer)
  ├── auth_router.py
  ├── wallet_router.py
  ├── payment_router.py
  ├── merchant_router.py
  ├── cashback_router.py
  └── reconciliation_router.py
        │
        ▼
Services (Business Logic Layer)
  ├── auth_service.py
  ├── wallet_service.py
  ├── payment_service.py
  ├── cashback_service.py
  ├── merchant_service.py
  └── reconciliation_service.py
        │
        ▼
Repositories (Data Access Queries)
  ├── user_repository.py
  ├── wallet_repository.py
  ├── transaction_repository.py
  ├── cashback_repository.py
  └── merchant_repository.py
        │
        ▼
Models (SQLAlchemy 3NF Entities)
        │
        ▼
SQLite Database (finpay.db)
```

### 2. Database Schema (3NF)

```
STUDENT ──────── (1 : 0..1) ──────── WALLET ──────── (1 : N) ──────── TRANSACTION
(StudentID, Name)                    (WalletID,                       (TransactionID,
                                      StudentID,                       WalletID,
                                      Tier,                            MerchantID,
                                      BalancePaise)                    IdempotencyKey,
                                         │                             AmountPaise,
                                         │ (N : 1)                     CashbackPaise,
                                         ▼                             CreatedAt)
                                    WALLET_TIER                            │
                                    (Tier,                                 │ (N : 1)
                                     RateMultX10,                          ▼
                                     CapMultX10)                        MERCHANT
                                                                        (MerchantID,
                                                                         BusinessName,
                                                                         Category)
                                                                           │
                                                                           │ (N : 1)
                                                                           ▼
                                                                     CASHBACK_RULE
                                                                     (Category,
                                                                      BaseRateBps,
                                                                      BaseMonthlyCapPaise)
```

---

## Running Automated Tests

FinPay includes a test suite verifying edge cases, boundary conditions, idempotency, and full payment flows using `pytest`:

```bash
pytest
```

### Tested Edge Cases Include:
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
11. Double-entry audit balance verification (`BALANCED`).

---

## Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **API Framework** | FastAPI (ASGI) |
| **Web Server** | Uvicorn |
| **ORM & Database** | SQLAlchemy & SQLite |
| **Security & Auth** | PyJWT (HMAC-SHA256) & PBKDF2/SHA256 password hashing |
| **Testing** | Pytest & HTTPX TestClient |
| **Frontend** | Vanilla JavaScript (ES6+), HTML5, Glassmorphic CSS |
