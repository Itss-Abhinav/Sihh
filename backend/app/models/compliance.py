from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class ComplianceResult(Base):
    __tablename__ = "compliance_results"

    id = Column(String, primary_key=True, index=True)
    scan_id = Column(String, ForeignKey("scans.id"), unique=True, nullable=False)
    overall_status = Column(String, nullable=False) # COMPLIANT, POTENTIAL_ISSUES_DETECTED, PARTIALLY_VERIFIED, UNABLE_TO_VERIFY
    
    total_checks = Column(Integer, default=0)
    passed_checks = Column(Integer, default=0)
    failed_checks = Column(Integer, default=0)
    unverified_checks = Column(Integer, default=0)
    not_applicable_checks = Column(Integer, default=0)
    
    disclaimer = Column(String, default="Automated screening result — not a legal determination.")
    execution_time_ms = Column(Float, default=0.0)

    scan = relationship("Scan", back_populates="compliance_result")

class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"

    id = Column(String, primary_key=True, index=True)
    scan_id = Column(String, ForeignKey("scans.id"), nullable=False, index=True)
    
    field = Column(String, nullable=False)
    status = Column(String, nullable=False) # PASS, FAIL, NOT_APPLICABLE, UNABLE_TO_VERIFY, REQUIRES_VERIFICATION
    detected_value = Column(Text, nullable=True)
    expected_requirement = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    rule_code = Column(String, nullable=False, index=True)
    source_reference = Column(String, nullable=False)
    category = Column(String, default="General")
    penalty_note = Column(Text, nullable=True)

    scan = relationship("Scan", back_populates="checks")
