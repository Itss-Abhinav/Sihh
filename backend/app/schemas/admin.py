import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.schemas.scan import ScanSummaryItem

class AdminViolationMetric(BaseModel):
    ruleCode: str
    ruleName: str
    occurrenceCount: int
    category: str

class CategoryMetric(BaseModel):
    category: str
    count: int

class AdminDashboardStats(BaseModel):
    totalScans: int
    compliantScans: int
    potentialIssueScans: int
    partiallyVerifiedScans: int
    unableToVerifyScans: int
    complianceRatePct: float
    commonPotentialViolations: List[AdminViolationMetric]
    categoryDistribution: List[CategoryMetric]
    recentScans: List[ScanSummaryItem]
    neutralNotice: str = "Automated compliance metrics reflecting recorded screening scans. Repeated potential compliance issues detected are screening observations, not legal adjudications."
