from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.app.database import get_db
from backend.app.models.scan import Scan
from backend.app.models.compliance import ComplianceCheck, ComplianceResult
from backend.app.schemas.admin import AdminDashboardStats, AdminViolationMetric, CategoryMetric
from backend.app.schemas.scan import ScanSummaryItem
from backend.app.services.rule_engine.rules_data import LEGAL_RULES

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])

@router.get("/dashboard", response_model=AdminDashboardStats)
def get_admin_dashboard_metrics(db: Session = Depends(get_db)):
    total_scans = db.query(Scan).count()
    compliant_scans = db.query(Scan).filter(Scan.overall_status == "COMPLIANT").count()
    potential_issues = db.query(Scan).filter(Scan.overall_status == "POTENTIAL_ISSUES_DETECTED").count()
    partially_verified = db.query(Scan).filter(Scan.overall_status == "PARTIALLY_VERIFIED").count()
    unable_to_verify = db.query(Scan).filter(Scan.overall_status == "UNABLE_TO_VERIFY").count()

    compliance_rate = round((compliant_scans / total_scans * 100), 1) if total_scans > 0 else 0.0

    # Common potential violations (neutral screening aggregation)
    violation_query = (
        db.query(
            ComplianceCheck.rule_code,
            func.count(ComplianceCheck.id).label("count")
        )
        .filter(ComplianceCheck.status == "FAIL")
        .group_by(ComplianceCheck.rule_code)
        .order_by(desc("count"))
        .limit(6)
        .all()
    )

    common_violations = []
    for row in violation_query:
        rule_info = LEGAL_RULES.get(row.rule_code, {})
        common_violations.append(AdminViolationMetric(
            ruleCode=row.rule_code,
            ruleName=rule_info.get("name", row.rule_code),
            occurrenceCount=row.count,
            category=rule_info.get("category", "General")
        ))

    # Category distribution
    cat_query = (
        db.query(
            Scan.category,
            func.count(Scan.id).label("count")
        )
        .filter(Scan.category.isnot(None))
        .group_by(Scan.category)
        .order_by(desc("count"))
        .limit(8)
        .all()
    )

    categories = [
        CategoryMetric(category=cat_name or "Unclassified", count=c)
        for cat_name, c in cat_query
    ]

    # Recent scans
    recent_records = db.query(Scan).order_by(desc(Scan.created_at)).limit(10).all()
    recent_scans = []
    for s in recent_records:
        res = s.compliance_result
        recent_scans.append(ScanSummaryItem(
            id=s.id,
            productName=s.product_name,
            brandName=s.brand_name,
            category=s.category,
            overallStatus=s.overall_status,
            failedCount=res.failed_checks if res else 0,
            passedCount=res.passed_checks if res else 0,
            createdAt=s.created_at
        ))

    return AdminDashboardStats(
        totalScans=total_scans,
        compliantScans=compliant_scans,
        potentialIssueScans=potential_issues,
        partiallyVerifiedScans=partially_verified,
        unableToVerifyScans=unable_to_verify,
        complianceRatePct=compliance_rate,
        commonPotentialViolations=common_violations,
        categoryDistribution=categories,
        recentScans=recent_scans,
        neutralNotice="Automated compliance metrics reflecting recorded screening scans. Repeated potential compliance issues detected are screening observations, not legal adjudications."
    )
