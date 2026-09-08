# LABELCHECK 🇮🇳

> **AI-Assisted Packaged Commodity Label Compliance Screening Application for India**  
> Evaluated deterministically against **The Legal Metrology (Packaged Commodities) Rules, 2011** and consolidated amendments (Development Rulebook Version **2026.2**).

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_18_+_TypeScript-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind_CSS_3.4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ⚖️ Statutory Notice
> **"Automated screening result — not a legal determination."**  
> LabelCheck is an automated compliance screening tool designed for initial risk assessment and regulatory surveillance. Compliance evaluations reflect deterministic rules configured under the Legal Metrology (Packaged Commodities) Rules, 2011. Final statutory verification requires physical inspection by authorized Legal Metrology inspectors.

---

## 🚀 Key Features

- **100% Deterministic Rule Engine**: AI/OCR is strictly used for character extraction. Legal compliance determinations are never delegated to probabilistic LLMs, completely eliminating statutory hallucinations.
- **Exhaustive Regulatory Rulebook (2026.2)**: Evaluates 21 statutory rules including Scope Exclusions (Rule 3), Small Measure Exemptions (Rule 26), Mandatory Declarations (Rule 6), Structural Postal Addresses (Rule 10(1)), Prohibited Qualifying Expressions (Rule 13), Third Schedule "when packed" restrictions, and Fourth Schedule commodity units.
- **Physical Inspection Boundaries**: Accurately flags measurements that cannot be determined by 2D camera images (e.g. font height in physical mm, 3D PDP ratio, adhesive sticker tampering, laboratory gravimetric error) as `UNABLE_TO_VERIFY` rather than guessing.
- **Polished SaaS UI**: Modern glassmorphism dark theme, interactive drag-and-drop file picker, mobile camera capture, animated multi-step screening pipeline, and print-ready compliance reports.
- **Surveillance & Admin Dashboard**: KPI tracking, category distributions, and recurring potential non-compliance patterns formulated using neutral statutory language.
- **Zero Secrets / Security Hardened**: Strict `.gitignore`, zero committed credentials, salted bcrypt password hashing, and role-based JWT authentication.

---

## 🏛️ System Architecture

```
User (Mobile / Desktop Browser)
            │
            ▼
┌─────────────────────────────────────────┐
│  Vercel Global Edge CDN                 │
│  React + TypeScript + Vite SPA          │
└─────────────────────────────────────────┘
            │  HTTPS REST / CORS
            ▼
┌─────────────────────────────────────────┐
│  Remote Web Service (Render Free Tier)  │
│  FastAPI + Python 3.11+ ASGI Container  │
│  - OcrService (Mock / Replaceable)      │
│  - LabelExtractionService (Replaceable) │
│  - Deterministic Rule Engine (2026.2)   │
└─────────────────────────────────────────┘
            │  SQLAlchemy ORM (Port 5432)
            ▼
┌─────────────────────────────────────────┐
│  Remote PostgreSQL Instance             │
│  Users, Scans, LabelData, Checks        │
└─────────────────────────────────────────┘
```

---

## 🧪 Pre-configured Benchmark Test Presets

LabelCheck includes 3 benchmark presets accessible via 1-click on the Scan page:
1. **Demo A (Mostly Compliant)**: *SunGold Butter Cookies* — standard 200g SI quantity, complete factory postal address with PIN, MRP with "inclusive of all taxes" clause, Unit Sale Price (USP), and dual-channel consumer grievance redressal.
2. **Demo B (Missing Manufacturer & Details)**: *Crunchy Nacho Crisps* — missing manufacturer postal premises address, missing consumer care helpline, price missing mandatory tax inclusion phrase.
3. **Demo C (Multiple Potential Violations)**: *Herbal Glow Body Wash* — contains prohibited qualifying term "approx", invalid "when packed" clause on liquid body wash (restricted exclusively to soaps/lotions/creams under Third Schedule), and abbreviated city-only address.

---

## 🔑 Pre-seeded Test Accounts

When running the application for the first time, default demonstration accounts are initialized automatically:

| Role | Email | Password | Permissions |
|---|---|---|---|
| **Admin** | `admin@labelcheck.in` | `Admin@12345` | Full system access & compliance surveillance analytics |
| **Inspector** | `inspector@lm.gov.in` | `Inspector@12345` | Inspection history & screening reports |
| **Retailer** | `retailer@store.in` | `Retailer@12345` | Merchant pack screening & history archive |
| **Consumer** | `demo@labelcheck.in` | `Demo@12345` | Public shopper screening access |

*(One-click autofill buttons are provided on the Login screen for instant access).*

---

## 💻 Local Development Setup

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** and **npm**

### 1. Clone the Repository
```bash
git clone https://github.com/Itss-Abhinav/Sihh.git
cd Sihh
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
# source venv/bin/activate

pip install -r requirements.txt
python run.py
```
Backend API will start at `http://localhost:8000`. OpenAPI documentation available at `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
Frontend development server will launch at `http://localhost:5173`.

---

## 🌐 Remote Cloud Deployment Guide

### A. Deploy Backend to Render (Free Tier)
1. Fork or push this repository to GitHub (`Itss-Abhinav/Sihh`).
2. Log in to [Render.com](https://render.com) with GitHub.
3. Click **New +** → **Blueprint**.
4. Select the `Itss-Abhinav/Sihh` repository. Render automatically reads `render.yaml` and sets up:
   - **`labelcheck-db`**: Free managed PostgreSQL database.
   - **`labelcheck-api`**: Free FastAPI web service configured with automatic connection string wiring.
5. Click **Apply**. Once deployed, copy your service URL (e.g. `https://labelcheck-api.onrender.com`).

*Free Tier Note: Render web services spin down after 15 minutes of inactivity. When a new scan request is made, the service automatically awakens within 30-50 seconds.*

### B. Deploy Frontend to Vercel
1. Log in to [Vercel.com](https://vercel.com).
2. Click **Add New** → **Project** → Select `Itss-Abhinav/Sihh`.
3. Set **Root Directory** to `frontend`.
4. Add Environment Variable:
   - `VITE_API_BASE_URL` = `https://labelcheck-api.onrender.com` (your remote backend URL)
5. Click **Deploy**. Vercel will build the React SPA and provide a global edge URL (e.g. `https://sihh.vercel.app`).

---

## 🔒 Security & Secret Management

- Strictly audited `.gitignore` prevents commit of `.env`, `credentials/`, `*.pem`, `*.key`, `service-account*.json`, or local `.db` files.
- Configuration template provided via `.env.example` with zero sensitive defaults.
- Passwords hashed with salted bcrypt rounds; JWT tokens signed with server-side secrets.
- CORS configured to accept deployed Vercel origins.

---

## 📚 Technical Documentation

- [docs/architecture.md](docs/architecture.md): Deep architectural overview, pipeline design, and remote hosting topology.
- [docs/api.md](docs/api.md): Complete REST endpoint reference and request/response models.
- [docs/rules.md](docs/rules.md): Regulatory mapping of Rulebook 2026.2 under Legal Metrology Rules, 2011.

---

## 📄 License
Released under the [MIT License](LICENSE).