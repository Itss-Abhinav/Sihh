import sys
import types
import os

# Module aliasing so imports work whether root is Sihh/ or backend/
if "backend" not in sys.modules:
    try:
        import backend
    except ImportError:
        _b = types.ModuleType("backend")
        sys.modules["backend"] = _b
        try:
            import app
            _b.app = app
            sys.modules["backend.app"] = app
        except ImportError:
            pass

import uuid
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.models.user import User
from backend.app.models.scan import Scan
from backend.app.models.label_data import LabelData
from backend.app.models.compliance import ComplianceResult, ComplianceCheck
from backend.app.auth.security import hash_password
from backend.app.services.ocr_service import MockOcrService
from backend.app.services.extraction_service import MockLabelExtractionService, normalize_mrp
from backend.app.services.rule_engine.engine import DeterministicRuleEngine
from backend.app.routers import auth_router, scans_router, rules_router, admin_router

def init_seed_data():
    db = SessionLocal()
    try:
        # Check users
        if db.query(User).count() == 0:
            users_to_seed = [
                ("admin@labelcheck.in", "Admin@12345", "System Administrator", "ADMIN"),
                ("inspector@lm.gov.in", "Inspector@12345", "Legal Metrology Inspector", "INSPECTOR"),
                ("retailer@store.in", "Retailer@12345", "Retail Store Manager", "RETAILER"),
                ("demo@labelcheck.in", "Demo@12345", "Consumer Tester", "CONSUMER"),
            ]
            for email, pwd, name, role in users_to_seed:
                u = User(
                    id=str(uuid.uuid4()),
                    email=email,
                    hashed_password=hash_password(pwd),
                    full_name=name,
                    role=role,
                    is_active=True
                )
                db.add(u)
            db.commit()

        # Seed initial demo scans if empty
        if db.query(Scan).count() == 0:
            ocr = MockOcrService()
            ext = MockLabelExtractionService()
            eng = DeterministicRuleEngine()

            demos = [
                ("demoA", "SunGold Butter Cookies", "SunGold", "Food & Confectionery"),
                ("demoB", "Crunchy Nacho Crisps", "Fiesta Snacks", "Snack Foods"),
                ("demoC", "Herbal Glow Body Wash", "GlowAura", "Personal Care")
            ]

            for preset, p_name, b_name, cat in demos:
                raw_text = ocr.get_demo_text(preset)
                payload = ext.extract_fields(raw_text, category_hint=cat)
                report = eng.evaluate(payload)
                scan_id = str(uuid.uuid4())

                scan = Scan(
                    id=scan_id,
                    user_id=None,
                    product_name=p_name,
                    brand_name=b_name,
                    category=cat,
                    overall_status=report.overallStatus,
                    image_filename=f"{preset}.jpg",
                    image_url=f"/static/demos/{preset}.jpg"
                )
                db.add(scan)

                lbl = LabelData(
                    id=str(uuid.uuid4()),
                    scan_id=scan_id,
                    product_name=p_name,
                    brand_name=b_name,
                    product_category=cat,
                    generic_name=payload.genericName.value,
                    mrp=payload.mrp.value,
                    mrp_normalized=normalize_mrp(payload.mrp.value),
                    net_quantity=payload.netQuantity.value,
                    quantity_unit=payload.quantityUnit.value,
                    manufacturer_name=payload.manufacturerName.value,
                    manufacturer_address=payload.manufacturerAddress.value,
                    packer_name=payload.packerName.value,
                    packer_address=payload.packerAddress.value,
                    importer_name=payload.importerName.value,
                    importer_address=payload.importerAddress.value,
                    manufacture_date=payload.manufactureDate.value,
                    import_date=payload.importDate.value,
                    consumer_care_name=payload.consumerCareName.value,
                    consumer_care_phone=payload.consumerCarePhone.value,
                    consumer_care_email=payload.consumerCareEmail.value,
                    consumer_care_address=payload.consumerCareAddress.value,
                    country_of_origin=payload.countryOfOrigin.value,
                    unit_sale_price=payload.unitSalePrice.value,
                    size_dimensions=payload.sizeDimensions.value,
                    raw_ocr_text=raw_text,
                    raw_extracted_json=json.dumps(payload.model_dump())
                )
                db.add(lbl)

                comp = ComplianceResult(
                    id=str(uuid.uuid4()),
                    scan_id=scan_id,
                    overall_status=report.overallStatus,
                    total_checks=report.summary["total"],
                    passed_checks=report.summary["passed"],
                    failed_checks=report.summary["failed"],
                    unverified_checks=report.summary["unable_to_verify"],
                    not_applicable_checks=report.summary["not_applicable"],
                    disclaimer=report.disclaimer,
                    execution_time_ms=report.executionTimeMs
                )
                db.add(comp)

                for chk in report.checks:
                    c = ComplianceCheck(
                        id=str(uuid.uuid4()),
                        scan_id=scan_id,
                        field=chk.field,
                        status=chk.status,
                        detected_value=chk.detectedValue,
                        expected_requirement=chk.expectedRequirement,
                        explanation=chk.explanation,
                        rule_code=chk.ruleCode,
                        source_reference=chk.sourceReference,
                        category=chk.category,
                        penalty_note=chk.penaltyNote
                    )
                    db.add(c)

            db.commit()
    except Exception as e:
        print(f"Error seeding initial data: {e}")
        db.rollback()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed data
    Base.metadata.create_all(bind=engine)
    init_seed_data()
    yield

app = FastAPI(
    title="LABELCHECK API",
    description="Legal Metrology (Packaged Commodities) Rules, 2011 Compliance Screening API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
origins = settings.cors_origins_list
if "*" in origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Routers
app.include_router(auth_router)
app.include_router(scans_router)
app.include_router(rules_router)
app.include_router(admin_router)

@app.get("/")
def root():
    return {
        "app": "LABELCHECK API",
        "version": "1.0.0",
        "rulebook": "2026.2",
        "legalDisclaimer": "Automated screening result — not a legal determination.",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "LABELCHECK"}
