import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from backend.app.schemas.rule import RuleCheckResult

class ScanCreateRequest(BaseModel):
    demoPreset: Optional[str] = None
    customText: Optional[str] = None
    productCategory: Optional[str] = None

class ScanSummaryItem(BaseModel):
    id: str
    productName: Optional[str] = None
    brandName: Optional[str] = None
    category: Optional[str] = None
    overallStatus: str
    failedCount: int = 0
    passedCount: int = 0
    createdAt: datetime.datetime

    class Config:
        from_attributes = True

class ScanDetailResponse(BaseModel):
    id: str
    userId: Optional[str] = None
    productName: Optional[str] = None
    brandName: Optional[str] = None
    category: Optional[str] = None
    overallStatus: str
    imageUrl: Optional[str] = None
    createdAt: datetime.datetime
    disclaimer: str = "Automated screening result — not a legal determination."
    
    summary: Dict[str, int]
    extractedData: Dict[str, Any]
    rawOcrText: str
    checks: List[RuleCheckResult]
    executionTimeMs: float = 0.0

    class Config:
        from_attributes = True
