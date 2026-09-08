# LABELCHECK System Architecture & Technical Design

## 1. Executive Summary
**LABELCHECK** is a production-grade, AI-assisted packaged commodity label compliance screening application designed specifically for India's regulatory framework under **The Legal Metrology (Packaged Commodities) Rules, 2011** and subsequent Gazette amendments.

### Core Architectural Principle: Deterministic Legal Evaluation
In high-stakes regulatory domains, Large Language Models (LLMs) and probabilistic AI must **never** independently determine legal compliance. An AI model can hallucinate exemptions, misinterpret metric tolerances, or invent statutory approvals.

Therefore, LABELCHECK enforces a strictly decoupled pipeline:
1. **OCR / Vision Layer**: Optical character isolation and raw text transcription.
2. **Structured Extraction Layer**: Entity recognition mapping text blocks into standardized Pydantic metrology models.
3. **Deterministic Legal Rule Engine (Rulebook 2026.2)**: 100% hard-coded Python rule logic evaluating statutory requirements with official Gazette citations.
4. **Compliance Report Synthesis**: Neutral, standardized screening evaluation with non-negotiable statutory disclaimers.

```
┌──────────────┐      ┌─────────────┐      ┌───────────────────────┐
│ Package      │ ───► │ OCR Service │ ───► │ Structured Extraction │
│ Photo/Preset │      │ Abstraction │      │ (Values, Units, Norm) │
└──────────────┘      └─────────────┘      └───────────────────────┘
                                                       │
                                                       ▼
┌──────────────────────┐      ┌─────────────────────────────────┐
│ Compliance Screening │ ◄─── │ Deterministic Legal Rule Engine │
│ Report & Persistence │      │ (Rules 1-26, Schedules I-IV)    │
└──────────────────────┘      └─────────────────────────────────┘
```

---

## 2. Remote Cloud Deployment Topology

To ensure the application remains fully accessible independently of any local machine, laptop power state, or active browser session, LABELCHECK is architected for remote cloud hosting:

```
[ User on Mobile / Desktop / Browser ]
                  │
                  ▼
   ┌──────────────────────────────┐
   │  Vercel Global Edge CDN      │
   │  React + TypeScript + Vite   │
   │  Static SPA Hosting          │
   └──────────────────────────────┘
                  │ HTTPS REST (CORS)
                  ▼
   ┌──────────────────────────────┐
   │  Remote Web Service (Render) │
   │  FastAPI + Python 3.11+      │
   │  Uvicorn ASGI Container      │
   └──────────────────────────────┘
                  │ TCP / SSL (Port 5432)
                  ▼
   ┌──────────────────────────────┐
   │  Remote PostgreSQL Instance  │
   │  Cloud Managed Database      │
   └──────────────────────────────┘
```

### Free Tier Lifecycle & Sleep Characteristics
- **Backend (Render Web Service)**: On the free tier, services automatically sleep after 15 minutes of inactivity. When a new screening request arrives, the service wakes up within 30-50 seconds. The frontend features an interactive, animated progress indicator that accommodates cold starts gracefully.
- **Database (Remote PostgreSQL)**: Persistent managed database retaining all user accounts, scans, and audit checks across restarts.

---

## 3. Replaceable Service Abstractions

### 3.1 OCR Service (`OcrService`)
Located at `backend/app/services/ocr_service.py`.
Defines an abstract base class with `extract_text(image_bytes: bytes, filename: Optional[str]) -> str`.
- **MVP Implementation (`MockOcrService`)**: Returns realistic, high-fidelity OCR text strings modeled after actual Indian packaged commodity labels, with benchmark presets (`demoA`, `demoB`, `demoC`).
- **Production Drop-in**: Can be swapped with Tesseract OCR (`pytesseract`), AWS Textract, Google Cloud Vision, or Azure AI Vision by implementing the single abstract method.

### 3.2 Label Extraction Service (`LabelExtractionService`)
Located at `backend/app/services/extraction_service.py`.
Defines an abstract base class returning an `ExtractedLabelPayload` where every field includes `value`, `confidence`, and `sourceText`.
- **MRP Normalization**: Normalizes currency formats (`₹50`, `Rs. 50.00`, `INR 50/-`) into clean decimal numbers (`50.00`).
- **Production Drop-in**: Can integrate specialized Named Entity Recognition (NER) models or fine-tuned extraction agents while keeping the downstream rule engine completely independent.

---

## 4. Database Schema & Data Models

- **User**: Authentication, role-based access control (`CONSUMER`, `RETAILER`, `INSPECTOR`, `ADMIN`), secure salted password hashes.
- **Scan**: Top-level scan record tracking product name, brand, category, timestamp, overall status, and foreign key relations.
- **Product**: Normalized product catalog entry.
- **LabelData**: Stores raw OCR text, structured extracted values (mrp, net quantity, unit, manufacturer, dates, addresses), and confidence scores.
- **ComplianceResult**: Aggregate screening metrics (total checks, passed, failed, unverified, not applicable, execution time).
- **ComplianceCheck**: Granular audit check for each rule (rule code, detected value, statutory requirement, legal explanation, official Gazette reference citation, Section 36 penalty note).

---

## 5. Security Principles & Hardening

1. **Zero Secret Footprint**: Zero credentials, tokens, passwords, or JWT secrets are stored in version control.
2. **Environment Variable Injection**: Configured via `.env` locally and remote environment variables in production.
3. **Password Security**: Native `bcrypt` hashing with salt rounds.
4. **Statutory Non-Liability**: Enforces mandatory disclaimer banner: *"Automated screening result — not a legal determination."*