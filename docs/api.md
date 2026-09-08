# LABELCHECK REST API Documentation

Base URL (Local): `http://127.0.0.1:8000`  
Interactive OpenAPI / Swagger UI: `http://127.0.0.1:8000/docs`  
ReDoc UI: `http://127.0.0.1:8000/redoc`

---

## 1. System Endpoints

### `GET /`
Returns service status, active regulatory version, and statutory disclaimer.
```json
{
  "app": "LABELCHECK API",
  "version": "1.0.0",
  "rulebook": "2026.2",
  "legalDisclaimer": "Automated screening result — not a legal determination.",
  "docs": "/docs",
  "health": "/health"
}
```

### `GET /health`
Health check endpoint for container orchestrators and monitoring probes.
```json
{
  "status": "healthy",
  "service": "LABELCHECK"
}
```

---

## 2. Authentication Endpoints (`/api/auth`)

### `POST /api/auth/register`
Register a new user account.
- **Request Body**:
```json
{
  "email": "inspector@lm.gov.in",
  "password": "SecurePassword@123",
  "full_name": "R. Sharma",
  "role": "INSPECTOR"
}
```
- **Response (201 Created)**: Returns bearer access token and serialized user object.

### `POST /api/auth/login`
Authenticate user with email and password.
- **Request Body**:
```json
{
  "email": "inspector@lm.gov.in",
  "password": "SecurePassword@123"
}
```
- **Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "token_type": "bearer",
  "user": {
    "id": "c1f7b0f1-...",
    "email": "inspector@lm.gov.in",
    "full_name": "R. Sharma",
    "role": "INSPECTOR",
    "is_active": true,
    "created_at": "2026-09-08T19:40:00Z"
  }
}
```

### `GET /api/auth/me`
Fetches authenticated user profile. Requires `Authorization: Bearer <token>`.

---

## 3. Screening & Scans Endpoints (`/api/scans`)

### `POST /api/scans`
Executes complete screening pipeline: Optical capture -> Structured extraction -> Deterministic Rulebook 2026.2 evaluation -> Database persistence.
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `image` (Optional File): Image file (JPG, JPEG, PNG, WEBP; max 15MB).
  - `demoPreset` (Optional Form String): `'demoA'` | `'demoB'` | `'demoC'`
  - `customText` (Optional Form String): Raw label text for custom testing.
  - `productCategory` (Optional Form String): E.g. `'Food & Confectionery'`
- **Response (201 Created)**: Complete `ScanDetailResponse` object.

### `GET /api/scans`
Lists screening history.
- **Query Parameters**:
  - `status` (Optional): E.g. `COMPLIANT`, `POTENTIAL_ISSUES_DETECTED`, `PARTIALLY_VERIFIED`, `UNABLE_TO_VERIFY`
  - `limit` (Default 50, max 100)
  - `offset` (Default 0)

### `GET /api/scans/{id}`
Returns granular report details including extracted attributes, raw OCR text, execution time, and individual compliance checks.

### `DELETE /api/scans/{id}`
Removes scan record from database. (Protected).

---

## 4. Legal Metrology Rules Catalog (`/api/rules`)

### `GET /api/rules`
Returns entire 2026.2 rule catalog with statutory citations, categories, descriptions, and Section 36 penalty advisory notes.

### `GET /api/rules/{rule_code}`
Returns metadata and statutory reference for a specific rule code (e.g. `RULE_6_1_E_MRP`).

---

## 5. Administrative Surveillance Analytics (`/api/admin`)

### `GET /api/admin/dashboard`
Returns high-level surveillance metrics:
- Overall scan volumes
- Compliant vs. potential issue ratios
- Common recurring potential non-compliances (using neutral screening terminology)
- Category distribution
- Recent scans summary