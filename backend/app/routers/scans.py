import uuid
import json
import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.scan import Scan
from backend.app.models.product import Product
from backend.app.models.label_data import LabelData
from backend.app.models.compliance import ComplianceResult, ComplianceCheck
from backend.app.schemas.scan import ScanSummaryItem, ScanDetailResponse
from backend.app.schemas.rule import RuleCheckResult
from backend.app.auth.dependencies import get_optional_current_user, get_current_user
from backend.app.services.ocr_service import MockOcrService
from backend.app.services.extraction_service import MockLabelExtractionService, normalize_mrp
from backend.app.services.rule_engine.engine import DeterministicRuleEngine

router = APIRouter(prefix="/api/scans", tags=["Scans & Compliance"])

ocr_service = MockOcrService()
extraction_service = MockLabelExtractionService()
rule_engine = DeterministicRuleEngine()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_IMAGE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB

@router.post("", response_model=ScanDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    image: Optional[UploadFile] = File(None),
    demoPreset: Optional[str] = Form(None),
    customText: Optional[str] = Form(None),
    productCategory: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    image_filename = None
    image_url = None
    ocr_text = ""

    # Helper: check if text looks like real packaging declarations (not OCR garbage)
    import re as _re
    def _is_quality_text(txt: str) -> bool:
        if not txt or len(txt.strip()) < 20:
            return False
        t = txt.lower()
        packaging_keywords = ['mrp', 'net', 'brand', 'product', 'mfg', 'manufactured', 'packed',
                              'address', 'consumer', 'country', 'origin', 'weight', 'quantity',
                              'price', 'ingredients', 'nutritional', 'best before', 'expiry',
                              'batch', 'lot', 'fssai', 'lic', 'toll free', '1800', 'email',
                              'pvt', 'ltd', 'limited', 'industries', 'biscuit', 'cookie']
        hits = sum(1 for kw in packaging_keywords if kw in t)
        return hits >= 3

    if image:
        # ALWAYS process the image via server-side OCR when an image is present
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image type: {image.content_type}. Allowed: JPG, JPEG, PNG, WEBP."
            )
        contents = await image.read()
        if len(contents) > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image size exceeds 15MB limit."
            )
        image_filename = image.filename or "uploaded_label.jpg"
        image_url = f"/uploads/{image_filename}"

        # Step A: Run server-side packaging OCR on the actual image
        server_ocr_text = ocr_service.extract_text(contents, image_filename)

        # Step B: Decide which text source to use
        if server_ocr_text and len(server_ocr_text.strip()) >= 15:
            ocr_text = server_ocr_text.strip()
        elif customText and _is_quality_text(customText):
            # Only use client-provided text if it contains real packaging keywords
            ocr_text = customText.strip()
        elif server_ocr_text and len(server_ocr_text.strip()) >= 5:
            ocr_text = server_ocr_text.strip()
        else:
            ocr_text = "Product: Scanned Packaged Commodity\nNote: Optical recognition detected low contrast or glare on packaging wrapper. Please review extracted declarations."

    elif customText and _is_quality_text(customText):
        # No image — user typed/pasted quality text with packaging keywords
        ocr_text = customText.strip()
        image_filename = "custom_text_input.txt"
    elif customText and customText.strip() and len(customText.strip()) >= 15:
        # Shorter text without keywords — still accept if no image
        ocr_text = customText.strip()
        image_filename = "custom_text_input.txt"
    elif demoPreset:
        ocr_text = ocr_service.get_demo_text(demoPreset)
        image_filename = f"{demoPreset}.jpg"
        image_url = f"/static/demos/{demoPreset}.jpg"
    else:
        # Default fallback to demoA
        ocr_text = ocr_service.get_demo_text("demoA")
        image_filename = "demoA.jpg"

    # Step 1: Structured Extraction
    extracted_payload = extraction_service.extract_fields(ocr_text, category_hint=productCategory)

    # Step 2: Deterministic Rule Engine
    report = rule_engine.evaluate(extracted_payload)

    # Step 3: Database Persistence
    scan_id = str(uuid.uuid4())
    p_name = extracted_payload.productName.value or "Packaged Commodity"
    b_name = extracted_payload.brandName.value or "Brand"
    cat_val = extracted_payload.productCategory.value or "General"

    # Record product
    existing_product = db.query(Product).filter(Product.name == p_name, Product.brand == b_name).first()
    if not existing_product:
        prod = Product(
            id=str(uuid.uuid4()),
            name=p_name,
            brand=b_name,
            category=cat_val
        )
        db.add(prod)

    # Record scan
    scan = Scan(
        id=scan_id,
        user_id=current_user.id if current_user else None,
        product_name=p_name,
        brand_name=b_name,
        category=cat_val,
        overall_status=report.overallStatus,
        image_filename=image_filename,
        image_url=image_url
    )
    db.add(scan)

    # Record label data
    label_entry = LabelData(
        id=str(uuid.uuid4()),
        scan_id=scan_id,
        product_name=p_name,
        brand_name=b_name,
        product_category=cat_val,
        generic_name=extracted_payload.genericName.value,
        mrp=extracted_payload.mrp.value,
        mrp_normalized=normalize_mrp(extracted_payload.mrp.value),
        net_quantity=extracted_payload.netQuantity.value,
        quantity_unit=extracted_payload.quantityUnit.value,
        manufacturer_name=extracted_payload.manufacturerName.value,
        manufacturer_address=extracted_payload.manufacturerAddress.value,
        packer_name=extracted_payload.packerName.value,
        packer_address=extracted_payload.packerAddress.value,
        importer_name=extracted_payload.importerName.value,
        importer_address=extracted_payload.importerAddress.value,
        manufacture_date=extracted_payload.manufactureDate.value,
        import_date=extracted_payload.importDate.value,
        consumer_care_name=extracted_payload.consumerCareName.value,
        consumer_care_phone=extracted_payload.consumerCarePhone.value,
        consumer_care_email=extracted_payload.consumerCareEmail.value,
        consumer_care_address=extracted_payload.consumerCareAddress.value,
        country_of_origin=extracted_payload.countryOfOrigin.value,
        unit_sale_price=extracted_payload.unitSalePrice.value,
        size_dimensions=extracted_payload.sizeDimensions.value,
        raw_ocr_text=ocr_text,
        confidence_scores_json=json.dumps({
            k: getattr(v, "confidence", 0.0)
            for k, v in extracted_payload.model_dump().items()
            if isinstance(v, dict) and "confidence" in v
        }),
        raw_extracted_json=json.dumps(extracted_payload.model_dump())
    )
    db.add(label_entry)

    # Record compliance result summary
    comp_result = ComplianceResult(
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
    db.add(comp_result)

    # Record individual compliance checks
    for chk in report.checks:
        c_entry = ComplianceCheck(
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
        db.add(c_entry)

    db.commit()

    return ScanDetailResponse(
        id=scan_id,
        userId=current_user.id if current_user else None,
        productName=p_name,
        brandName=b_name,
        category=cat_val,
        overallStatus=report.overallStatus,
        imageUrl=image_url,
        createdAt=scan.created_at,
        disclaimer=report.disclaimer,
        summary=report.summary,
        extractedData=extracted_payload.model_dump(),
        rawOcrText=ocr_text,
        checks=report.checks,
        executionTimeMs=report.executionTimeMs
    )
@router.get("", response_model=List[ScanSummaryItem])
def list_scans(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Scan)
    
    # If user is not admin or inspector, scope to their own scans if authenticated
    if current_user and current_user.role not in ["ADMIN", "INSPECTOR"]:
        query = query.filter(Scan.user_id == current_user.id)
    
    if status:
        query = query.filter(Scan.overall_status == status.upper())

    scans = query.order_by(desc(Scan.created_at)).offset(offset).limit(limit).all()
    
    results = []
    for s in scans:
        res = s.compliance_result
        results.append(ScanSummaryItem(
            id=s.id,
            productName=s.product_name,
            brandName=s.brand_name,
            category=s.category,
            overallStatus=s.overall_status,
            failedCount=res.failed_checks if res else 0,
            passedCount=res.passed_checks if res else 0,
            createdAt=s.created_at
        ))
    return results

@router.get("/{scan_id}", response_model=ScanDetailResponse)
def get_scan_details(scan_id: str, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan record not found")

    label = scan.label_data
    res = scan.compliance_result
    checks = scan.checks

    summary = {
        "total": res.total_checks if res else 0,
        "passed": res.passed_checks if res else 0,
        "failed": res.failed_checks if res else 0,
        "unable_to_verify": res.unverified_checks if res else 0,
        "not_applicable": res.not_applicable_checks if res else 0,
    }

    extracted_data = {}
    if label and label.raw_extracted_json:
        try:
            extracted_data = json.loads(label.raw_extracted_json)
        except Exception:
            pass

    rule_checks = []
    for c in checks:
        rule_checks.append(RuleCheckResult(
            field=c.field,
            status=c.status,
            detectedValue=c.detected_value,
            expectedRequirement=c.expected_requirement,
            explanation=c.explanation,
            ruleCode=c.rule_code,
            sourceReference=c.source_reference,
            category=c.category or "General",
            penaltyNote=c.penalty_note
        ))

    return ScanDetailResponse(
        id=scan.id,
        userId=scan.user_id,
        productName=scan.product_name,
        brandName=scan.brand_name,
        category=scan.category,
        overallStatus=scan.overall_status,
        imageUrl=scan.image_url,
        createdAt=scan.created_at,
        disclaimer=res.disclaimer if res else "Automated screening result — not a legal determination.",
        summary=summary,
        extractedData=extracted_data,
        rawOcrText=label.raw_ocr_text if label else "",
        checks=rule_checks,
        executionTimeMs=res.execution_time_ms if res else 0.0
    )

@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scan(scan_id: str, current_user: Optional[User] = Depends(get_optional_current_user), db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    if current_user and current_user.role not in ["ADMIN", "INSPECTOR"] and scan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this scan")

    db.delete(scan)
    db.commit()
    return None
