import abc
import re
from typing import Optional, Dict, Any
from backend.app.schemas.rule import ExtractedField, ExtractedLabelPayload

def normalize_mrp(raw_mrp: Optional[str]) -> Optional[str]:
    if not raw_mrp:
        return None
    # Matches patterns like ₹50, Rs. 50.00, INR 120, 50/-, 50.00
    cleaned = re.sub(r'[₹Rs\.INRF\s/-]', '', raw_mrp, flags=re.IGNORECASE)
    match = re.search(r'(\d+(?:\.\d{1,2})?)', cleaned)
    if match:
        try:
            val = float(match.group(1))
            return f"{val:.2f}"
        except ValueError:
            return None
    return None

class LabelExtractionService(abc.ABC):
    """Abstract base class for extracting structured Legal Metrology fields from OCR text."""
    
    @abc.abstractmethod
    def extract_fields(self, ocr_text: str, category_hint: Optional[str] = None) -> ExtractedLabelPayload:
        pass

class MockLabelExtractionService(LabelExtractionService):
    """
    Production-grade rule-based and pattern-matching structured extraction service.
    Can extract structured fields from arbitrary OCR text and normalized formats.
    """

    def extract_fields(self, ocr_text: str, category_hint: Optional[str] = None) -> ExtractedLabelPayload:
        lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]
        
        def find_pattern(regex: str, group_idx: int = 1) -> Optional[tuple[str, str]]:
            for line in lines:
                m = re.search(regex, line, re.IGNORECASE)
                if m:
                    val = m.group(group_idx).strip()
                    return val, line
            return None

        # 1. Product Name
        p_name = find_pattern(r'(?:Product|Commodity|Item|Name)\s*[:\-]?\s*(.+)')
        product_name = ExtractedField(
            value=p_name[0] if p_name else (lines[0] if lines else "Packaged Commodity"),
            confidence=0.95 if p_name else 0.70,
            sourceText=p_name[1] if p_name else (lines[0] if lines else "")
        )

        # 2. Brand Name
        b_name = find_pattern(r'(?:Brand|Trademark)\s*[:\-]?\s*(.+)')
        brand_name = ExtractedField(
            value=b_name[0] if b_name else "Generic Brand",
            confidence=0.92 if b_name else 0.60,
            sourceText=b_name[1] if b_name else ""
        )

        # 3. Category
        c_match = find_pattern(r'(?:Category|Type)\s*[:\-]?\s*(.+)')
        cat_val = category_hint or (c_match[0] if c_match else "General Commodity")
        product_category = ExtractedField(
            value=cat_val,
            confidence=0.90,
            sourceText=c_match[1] if c_match else ""
        )

        # 4. Generic Name
        g_name = find_pattern(r'(?:Generic\s*Name|Common\s*Name)\s*[:\-]?\s*(.+)')
        generic_name = ExtractedField(
            value=g_name[0] if g_name else None,
            confidence=0.93 if g_name else 0.0,
            sourceText=g_name[1] if g_name else None
        )

        # 5. MRP
        # Look for MRP lines
        mrp_match = find_pattern(r'(?:MRP|Maximum\s*Retail\s*Price|Max\.\s*Retail\s*Price)\s*[:\-]?\s*(.+)')
        mrp_val = None
        mrp_source = None
        if mrp_match:
            mrp_val = mrp_match[0]
            mrp_source = mrp_match[1]
        else:
            # Fallback search for ₹ or Rs.
            fallback = find_pattern(r'([₹Rs\.INR]+\s*[\d\.,]+(?:\s*inclusive\s*of\s*all\s*taxes)?)')
            if fallback:
                mrp_val = fallback[0]
                mrp_source = fallback[1]

        mrp = ExtractedField(
            value=mrp_val,
            confidence=0.95 if mrp_val else 0.0,
            sourceText=mrp_source
        )

        # 6. Net Quantity & Unit
        qty_match = find_pattern(r'(?:Net\s*Quantity|Net\s*Qty|Net\s*Wt\.?|Net\s*Weight|Net\s*Content)\s*[:\-]?\s*(.+)')
        net_qty_val = None
        qty_source = None
        qty_unit = None

        if qty_match:
            net_qty_val = qty_match[0]
            qty_source = qty_match[1]
        else:
            # Look for number + standard unit
            raw_qty = find_pattern(r'(\b\d+(?:\.\d+)?\s*(?:kg|g|ml|l|cm|m|N|U|units)\b)')
            if raw_qty:
                net_qty_val = raw_qty[0]
                qty_source = raw_qty[1]

        if net_qty_val:
            u_match = re.search(r'\b(kg|g|ml|l|L|cm|m|sq_dm|sq_m|cu_cm|cu_m|N|U|units?)\b', net_qty_val, re.IGNORECASE)
            if u_match:
                qty_unit = u_match.group(1).lower()

        net_quantity = ExtractedField(
            value=net_qty_val,
            confidence=0.95 if net_qty_val else 0.0,
            sourceText=qty_source
        )
        quantity_unit = ExtractedField(
            value=qty_unit,
            confidence=0.90 if qty_unit else 0.0,
            sourceText=qty_source
        )

        # 7. Manufacturer Details
        mfg_name_match = find_pattern(r'(?:Manufactured\s*(?:&|and)?\s*Packed\s*by|Manufactured\s*by|Mfd\s*by)\s*[:\-]?\s*(.+)')
        mfg_addr_match = find_pattern(r'(?:Address|Factory\s*Address|Mfg\s*Unit|Plot\s*No|Survey\s*No)\s*[:\-]?\s*(.+)')
        
        manufacturer_name = ExtractedField(
            value=mfg_name_match[0] if mfg_name_match else None,
            confidence=0.92 if mfg_name_match else 0.0,
            sourceText=mfg_name_match[1] if mfg_name_match else None
        )
        manufacturer_address = ExtractedField(
            value=mfg_addr_match[0] if mfg_addr_match else None,
            confidence=0.88 if mfg_addr_match else 0.0,
            sourceText=mfg_addr_match[1] if mfg_addr_match else None
        )

        # 8. Packer / Importer Details
        packer_match = find_pattern(r'(?:Packed\s*by|Pkd\s*by)\s*[:\-]?\s*(.+)')
        packer_name = ExtractedField(
            value=packer_match[0] if packer_match else None,
            confidence=0.89 if packer_match else 0.0,
            sourceText=packer_match[1] if packer_match else None
        )
        packer_address = ExtractedField(
            value=None,
            confidence=0.0,
            sourceText=None
        )

        importer_match = find_pattern(r'(?:Imported\s*by|Importer)\s*[:\-]?\s*(.+)')
        importer_name = ExtractedField(
            value=importer_match[0] if importer_match else None,
            confidence=0.91 if importer_match else 0.0,
            sourceText=importer_match[1] if importer_match else None
        )
        importer_address = ExtractedField(
            value=None,
            confidence=0.0,
            sourceText=None
        )

        # 9. Dates
        mfg_date_match = find_pattern(r'(?:Mfg\s*Date|Date\s*of\s*Mfg|Date\s*of\s*Packing|Pkd\s*Date|Manufacturing\s*Date|Packed\s*on)\s*[:\-]?\s*(.+)')
        manufacture_date = ExtractedField(
            value=mfg_date_match[0] if mfg_date_match else None,
            confidence=0.94 if mfg_date_match else 0.0,
            sourceText=mfg_date_match[1] if mfg_date_match else None
        )
        import_date = ExtractedField(
            value=None,
            confidence=0.0,
            sourceText=None
        )

        # 10. Consumer Care
        care_name_match = find_pattern(r'(?:Customer\s*Care|Consumer\s*Care|Consumer\s*Complaints)\s*[:\-]?\s*(.+)')
        care_phone_match = find_pattern(r'(?:Toll\s*Free|Phone|Tel|Helpline|Call)\s*[:\-]?\s*([0-9\-\+\s]{7,15})')
        care_email_match = find_pattern(r'(?:Email|Mail|E-mail)\s*[:\-]?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')
        
        consumer_care_name = ExtractedField(
            value=care_name_match[0] if care_name_match else None,
            confidence=0.90 if care_name_match else 0.0,
            sourceText=care_name_match[1] if care_name_match else None
        )
        consumer_care_phone = ExtractedField(
            value=care_phone_match[0] if care_phone_match else None,
            confidence=0.94 if care_phone_match else 0.0,
            sourceText=care_phone_match[1] if care_phone_match else None
        )
        consumer_care_email = ExtractedField(
            value=care_email_match[0] if care_email_match else None,
            confidence=0.96 if care_email_match else 0.0,
            sourceText=care_email_match[1] if care_email_match else None
        )
        consumer_care_address = ExtractedField(
            value=mfg_addr_match[0] if mfg_addr_match and care_name_match else None,
            confidence=0.80 if mfg_addr_match and care_name_match else 0.0,
            sourceText=mfg_addr_match[1] if mfg_addr_match and care_name_match else None
        )

        # 11. Country of Origin
        coo_match = find_pattern(r'(?:Country\s*of\s*Origin|Made\s*in)\s*[:\-]?\s*(.+)')
        country_of_origin = ExtractedField(
            value=coo_match[0] if coo_match else None,
            confidence=0.95 if coo_match else 0.0,
            sourceText=coo_match[1] if coo_match else None
        )

        # 12. Unit Sale Price
        usp_match = find_pattern(r'(?:Unit\s*Sale\s*Price|USP)\s*[:\-]?\s*(.+)')
        unit_sale_price = ExtractedField(
            value=usp_match[0] if usp_match else None,
            confidence=0.92 if usp_match else 0.0,
            sourceText=usp_match[1] if usp_match else None
        )

        # 13. Size Dimensions
        size_match = find_pattern(r'(?:Dimensions?|Size)\s*[:\-]?\s*(.+)')
        size_dimensions = ExtractedField(
            value=size_match[0] if size_match else None,
            confidence=0.88 if size_match else 0.0,
            sourceText=size_match[1] if size_match else None
        )

        return ExtractedLabelPayload(
            productName=product_name,
            brandName=brand_name,
            productCategory=product_category,
            genericName=generic_name,
            mrp=mrp,
            netQuantity=net_quantity,
            quantityUnit=quantity_unit,
            manufacturerName=manufacturer_name,
            manufacturerAddress=manufacturer_address,
            packerName=packer_name,
            packerAddress=packer_address,
            importerName=importer_name,
            importerAddress=importer_address,
            manufactureDate=manufacture_date,
            importDate=import_date,
            consumerCareName=consumer_care_name,
            consumerCarePhone=consumer_care_phone,
            consumerCareEmail=consumer_care_email,
            consumerCareAddress=consumer_care_address,
            countryOfOrigin=country_of_origin,
            unitSalePrice=unit_sale_price,
            sizeDimensions=size_dimensions,
            rawOcrText=ocr_text
        )
