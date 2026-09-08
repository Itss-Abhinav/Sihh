from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class LabelData(Base):
    __tablename__ = "label_data"

    id = Column(String, primary_key=True, index=True)
    scan_id = Column(String, ForeignKey("scans.id"), unique=True, nullable=False)
    
    product_name = Column(String, nullable=True)
    brand_name = Column(String, nullable=True)
    product_category = Column(String, nullable=True)
    generic_name = Column(String, nullable=True)
    
    mrp = Column(String, nullable=True)
    mrp_normalized = Column(String, nullable=True)
    net_quantity = Column(String, nullable=True)
    quantity_unit = Column(String, nullable=True)
    
    manufacturer_name = Column(String, nullable=True)
    manufacturer_address = Column(Text, nullable=True)
    packer_name = Column(String, nullable=True)
    packer_address = Column(Text, nullable=True)
    importer_name = Column(String, nullable=True)
    importer_address = Column(Text, nullable=True)
    
    manufacture_date = Column(String, nullable=True)
    import_date = Column(String, nullable=True)
    
    consumer_care_name = Column(String, nullable=True)
    consumer_care_phone = Column(String, nullable=True)
    consumer_care_email = Column(String, nullable=True)
    consumer_care_address = Column(Text, nullable=True)
    
    country_of_origin = Column(String, nullable=True)
    unit_sale_price = Column(String, nullable=True)
    size_dimensions = Column(String, nullable=True)
    
    raw_ocr_text = Column(Text, nullable=True)
    confidence_scores_json = Column(Text, nullable=True)
    raw_extracted_json = Column(Text, nullable=True)

    scan = relationship("Scan", back_populates="label_data")
