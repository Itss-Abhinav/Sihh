from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class RuleCheckResult(BaseModel):
    field: str
    status: str # PASS, FAIL, NOT_APPLICABLE, UNABLE_TO_VERIFY, REQUIRES_VERIFICATION
    detectedValue: Optional[str] = None
    expectedRequirement: str
    explanation: str
    ruleCode: str
    sourceReference: str
    category: str = "General"
    penaltyNote: Optional[str] = None

class ExtractedField(BaseModel):
    value: Optional[str] = None
    confidence: float = 0.0
    sourceText: Optional[str] = None

class ExtractedLabelPayload(BaseModel):
    productName: ExtractedField = Field(default_factory=ExtractedField)
    brandName: ExtractedField = Field(default_factory=ExtractedField)
    productCategory: ExtractedField = Field(default_factory=ExtractedField)
    genericName: ExtractedField = Field(default_factory=ExtractedField)
    mrp: ExtractedField = Field(default_factory=ExtractedField)
    netQuantity: ExtractedField = Field(default_factory=ExtractedField)
    quantityUnit: ExtractedField = Field(default_factory=ExtractedField)
    manufacturerName: ExtractedField = Field(default_factory=ExtractedField)
    manufacturerAddress: ExtractedField = Field(default_factory=ExtractedField)
    packerName: ExtractedField = Field(default_factory=ExtractedField)
    packerAddress: ExtractedField = Field(default_factory=ExtractedField)
    importerName: ExtractedField = Field(default_factory=ExtractedField)
    importerAddress: ExtractedField = Field(default_factory=ExtractedField)
    manufactureDate: ExtractedField = Field(default_factory=ExtractedField)
    importDate: ExtractedField = Field(default_factory=ExtractedField)
    consumerCareName: ExtractedField = Field(default_factory=ExtractedField)
    consumerCarePhone: ExtractedField = Field(default_factory=ExtractedField)
    consumerCareEmail: ExtractedField = Field(default_factory=ExtractedField)
    consumerCareAddress: ExtractedField = Field(default_factory=ExtractedField)
    countryOfOrigin: ExtractedField = Field(default_factory=ExtractedField)
    unitSalePrice: ExtractedField = Field(default_factory=ExtractedField)
    sizeDimensions: ExtractedField = Field(default_factory=ExtractedField)
    rawOcrText: str = ""

class ComplianceReport(BaseModel):
    overallStatus: str # COMPLIANT, POTENTIAL_ISSUES_DETECTED, PARTIALLY_VERIFIED, UNABLE_TO_VERIFY
    disclaimer: str = "Automated screening result — not a legal determination."
    summary: Dict[str, int]
    checks: List[RuleCheckResult]
    extractedData: Dict[str, Any]
    rawOcrText: str
    executionTimeMs: float = 0.0
