import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Scan(Base):
    __tablename__ = "scans"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    product_name = Column(String, nullable=True)
    brand_name = Column(String, nullable=True)
    category = Column(String, nullable=True)
    overall_status = Column(String, nullable=False, default="UNABLE_TO_VERIFY") # COMPLIANT, POTENTIAL_ISSUES_DETECTED, PARTIALLY_VERIFIED, UNABLE_TO_VERIFY
    image_filename = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    # Relationships
    label_data = relationship("LabelData", back_populates="scan", uselist=False, cascade="all, delete-orphan")
    compliance_result = relationship("ComplianceResult", back_populates="scan", uselist=False, cascade="all, delete-orphan")
    checks = relationship("ComplianceCheck", back_populates="scan", cascade="all, delete-orphan")
