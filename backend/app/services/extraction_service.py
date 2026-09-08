import abc
import re
from typing import Optional, Dict, Any, List
from backend.app.schemas.rule import ExtractedField, ExtractedLabelPayload

def normalize_mrp(raw_mrp: Optional[str]) -> Optional[str]:
    if not raw_mrp:
        return None
    # Must contain at least one digit
    match = re.search(r'(\d+(?:\.\d{1,2})?)', raw_mrp)
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
    Robust, production-grade pattern matching structured extraction service.
    Handles real-world smartphone label OCR with fuzzy matching, packaging keywords,
    Indian commodity heuristics, and Legal Metrology declaration standards.
    """

    def extract_fields(self, ocr_text: str, category_hint: Optional[str] = None) -> ExtractedLabelPayload:
        raw_text = ocr_text or ""
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        full_text = " \n ".join(lines)

        def search_patterns(patterns: List[str], text_to_search: Optional[str] = None) -> Optional[tuple[str, str]]:
            target = text_to_search if text_to_search is not None else full_text
            for p in patterns:
                m = re.search(p, target, re.IGNORECASE)
                if m:
                    val = m.group(1).strip()
                    cleaned = re.sub(r'[\s\.,:\-_/\(\)]', '', val)
                    if cleaned:
                        return val, m.group(0).strip()
            return None

        def search_lines(patterns: List[str]) -> Optional[tuple[str, str]]:
            for p in patterns:
                for line in lines:
                    m = re.search(p, line, re.IGNORECASE)
                    if m:
                        val = m.group(1).strip()
                        cleaned = re.sub(r'[\s\.,:\-_/\(\)]', '', val)
                        if cleaned:
                            return val, line
            return None

        # -------------------------------------------------------------
        # 1. Generic Name / Commodity (Rule 6(1)(b))
        # -------------------------------------------------------------
        g_patterns = [
            r'(?:Generic\s*Name|Common\s*Name|Commodity\s*Name|Product\s*Name)\s*[:\-]?\s*(.+)',
            r'^(?:Generic|Common)\s*[:\-]?\s*(.+)',
        ]
        g_name_match = search_lines(g_patterns)
        generic_val = None
        generic_source = None

        if g_name_match:
            generic_val = g_name_match[0]
            generic_source = g_name_match[1]
        else:
            # Fuzzy match standard packaged commodity keywords (e.g. Biscuits, Cookies, etc.)
            comm_match = re.search(
                r'\b(Butter\s*Cookies|Glucose\s*Biscuits|Digestive\s*Biscuits|Marie\s*Biscuits|Cream\s*Biscuits|Biscuits|Cookies|Crackers|Rusk|Wafers?|Noodles|Pasta|Snacks?|Namkeen|Chips|Crisps|Chocolates?|Bread|Cakes?|Body\s*Wash|Face\s*Wash|Soaps?|Shampoos?|Hair\s*Oil|Skin\s*Cream|Lotions?|Atta|Flours?|Edible\s*Oil|Tea|Coffee|Bottled\s*Water)\b',
                full_text,
                re.IGNORECASE
            )
            if comm_match:
                generic_val = comm_match.group(1).strip()
                generic_source = comm_match.group(0).strip()

        generic_name = ExtractedField(
            value=generic_val,
            confidence=0.92 if g_name_match else (0.85 if generic_val else 0.0),
            sourceText=generic_source
        )

        # -------------------------------------------------------------
        # 2. Brand Name
        # -------------------------------------------------------------
        b_patterns = [
            r'(?:Brand(?:\s*Name)?|Trademark|Trade\s*Name)\s*[:\-]?\s*(.+)',
        ]
        b_name_match = search_lines(b_patterns)
        brand_val = None
        brand_source = None

        if b_name_match:
            brand_val = b_name_match[0]
            brand_source = b_name_match[1]
        else:
            # Detect well-known FMCG brands in India
            fmcg_brand = re.search(
                r'\b(Britannia|Parle-G|Parle|Sunfeast|Good\s*Day|Marie\s*Gold|Oreo|Cadbury|Amul|Nestle|Mondelez|Haldirams?|Bikaji|Lays|Kurkure|Patanjali|Dabur|Hindustan\s*Unilever|HUL|ITC\s*Limited|ITC|Marico|Godrej|SunGold|Fiesta\s*Snacks|GlowAura|NatureBake)\b',
                full_text,
                re.IGNORECASE
            )
            if fmcg_brand:
                brand_val = fmcg_brand.group(1).strip()
                brand_source = fmcg_brand.group(0).strip()
            elif lines:
                brand_val = lines[0].strip()

        brand_name = ExtractedField(
            value=brand_val or "Packaged Commodity",
            confidence=0.92 if b_name_match else (0.85 if brand_source else 0.60),
            sourceText=brand_source or (lines[0] if lines else "")
        )

        # -------------------------------------------------------------
        # 3. Product Name (Rule 6(1)(a))
        # -------------------------------------------------------------
        p_patterns = [
            r'(?:Product(?:\s*Name)?|Commodity|Item(?:\s*Name)?)\s*[:\-]?\s*(.+)',
        ]
        p_name_match = search_lines(p_patterns)
        prod_val = None
        prod_source = None

        if p_name_match:
            prod_val = p_name_match[0]
            prod_source = p_name_match[1]
        elif brand_val and generic_val and brand_val.lower() not in generic_val.lower():
            prod_val = f"{brand_val} {generic_val}"
            prod_source = f"{brand_val} {generic_val}"
        elif lines:
            prod_val = lines[0]
            prod_source = lines[0]

        product_name = ExtractedField(
            value=prod_val or "Packaged Commodity",
            confidence=0.95 if p_name_match else 0.75,
            sourceText=prod_source or ""
        )

        # -------------------------------------------------------------
        # 4. Commodity Category
        # -------------------------------------------------------------
        cat_val = category_hint or "General Commodity"
        if generic_val:
            g_low = generic_val.lower()
            if any(w in g_low for w in ['biscuit', 'cookie', 'cracker', 'rusk', 'wafer', 'confection', 'cake']):
                cat_val = "Food & Confectionery"
            elif any(w in g_low for w in ['soap', 'wash', 'shampoo', 'cream', 'lotion', 'oil']):
                cat_val = "Personal Care"
            elif any(w in g_low for w in ['chip', 'snack', 'namkeen', 'noodle', 'pasta']):
                cat_val = "Snack Foods"
            elif any(w in g_low for w in ['tea', 'coffee', 'water', 'beverage', 'juice']):
                cat_val = "Beverages"

        product_category = ExtractedField(
            value=cat_val,
            confidence=0.90,
            sourceText=""
        )

        # -------------------------------------------------------------
        # 5. Maximum Retail Price (MRP) (Rule 6(1)(e))
        # -------------------------------------------------------------
        # Must strictly contain at least one digit (prevents bogus 'IR,' false positives)
        mrp_patterns = [
            r'(?:M\.?R\.?P\.?|Maximum\s*Retail\s*Price|Max\.\s*Retail\s*Price|RPS|PRICE)\s*[:\.\-]?\s*([₹RsINR\.\s]*\d+(?:\.\d{1,2})?(?:\s*\/-)?(?:\s*\(?(?:INCL|INCLUSIVE)[^\n\r\)]*\)?)?)',
            r'([₹RsINR\.]+\s*\d+(?:\.\d{1,2})?(?:\s*\/-)?(?:\s*\(?(?:INCL|INCLUSIVE)[^\n\r\)]*\)?)?)',
            r'(\b\d{1,4}\.\d{2}\b(?:\s*\(?(?:INCL|INCLUSIVE)[^\n\r\)]*\)?))',
        ]
        mrp_match = search_patterns(mrp_patterns)
        mrp_val = None
        mrp_source = None

        if mrp_match and re.search(r'\d', mrp_match[0]):
            mrp_val = mrp_match[0]
            mrp_source = mrp_match[1]

        mrp = ExtractedField(
            value=mrp_val,
            confidence=0.95 if mrp_val else 0.0,
            sourceText=mrp_source
        )

        # -------------------------------------------------------------
        # 6. Net Quantity & Unit (Rule 6(1)(c) & Rule 12)
        # -------------------------------------------------------------
        qty_line_patterns = [
            r'(?:Net\s*Quantity|Net\s*Qty|Net\s*Wt\.?|Net\s*Weight|Net\s*Content)\s*[:\.\-]?\s*(.+)',
        ]
        qty_match = search_lines(qty_line_patterns)
        net_qty_val = None
        qty_source = None
        qty_unit = None

        if qty_match:
            net_qty_val = qty_match[0]
            qty_source = qty_match[1]
        else:
            fallback_qty = search_patterns([
                r'(?:Weight|Qty)\s*[:\.\-]?\s*(\b\d+(?:\.\d+)?\s*(?:kg|g|gm|gms|gram|grams|ml|l|ltr|litres?)\b)',
                r'(\b\d+(?:\.\d+)?\s*(?:kg|g|gm|gms|gram|grams|ml|l|ltr|litres?)\b)'
            ])
            if fallback_qty:
                candidate_qty = fallback_qty[0]
                if not re.match(r'^(?:202[0-9]|19[0-9]{2})$', candidate_qty.strip()):
                    net_qty_val = candidate_qty
                    qty_source = fallback_qty[1]

        if net_qty_val:
            u_m = re.search(r'(?:[0-9]+(?:\.[0-9]+)?\s*)?(kg|g|gm|gms|gram|grams|ml|l|ltr|litres?|cm|m|sq_dm|sq_m|cu_cm|cu_m|N|U|units?)\b', net_qty_val, re.IGNORECASE)
            if u_m:
                raw_u = u_m.group(1).lower()
                if raw_u in ['gm', 'gms', 'gram', 'grams']:
                    qty_unit = 'g'
                elif raw_u in ['ltr', 'litres', 'litre']:
                    qty_unit = 'l'
                else:
                    qty_unit = raw_u

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

        # -------------------------------------------------------------
        # 7. Unit Sale Price (USP) (Rule 6(11))
        # -------------------------------------------------------------
        usp_patterns = [
            r'(?:Unit\s*Sale\s*Price|USP|Unit\s*Price)\s*[:\.\-]?\s*([₹RsINR\.\s]*\d+(?:\.\d{1,4})?\s*(?:per|\/)\s*[a-zA-Z]+)',
            r'([₹RsINR\.\s]*\d+(?:\.\d{1,4})?\s*(?:per|\/)\s*(?:g|gm|kg|ml|l|unit|piece|N))',
        ]
        usp_match = search_patterns(usp_patterns)
        unit_sale_price = ExtractedField(
            value=usp_match[0] if usp_match else None,
            confidence=0.92 if usp_match else 0.0,
            sourceText=usp_match[1] if usp_match else None
        )

        # -------------------------------------------------------------
        # 8. Manufacturer & Packer Details (Rule 6(1)(a) & Rule 10(1))
        # -------------------------------------------------------------
        mfg_name_patterns = [
            r'(?:Manufactured\s*(?:&|and)?\s*Packed\s*by|Manufactured\s*by|Mfd\s*by|Marketed\s*by)\s*[:\.\-]?\s*([^,\n\r]+(?:Private\s*Limited|Pvt\.?\s*Ltd\.?|Limited|Ltd\.?|Industries|Products|Foods|Bakeries|Confectionery)?)',
            r'\b([A-Z][A-Za-z0-9\s,\.\-&]{2,40}(?:Private\s*Limited|Pvt\.?\s*Ltd\.?|Limited|Ltd\.?|Industries|Foods|Bakeries))\b',
        ]
        mfg_name_match = search_patterns(mfg_name_patterns)
        manufacturer_name = ExtractedField(
            value=mfg_name_match[0] if mfg_name_match else None,
            confidence=0.92 if mfg_name_match else 0.0,
            sourceText=mfg_name_match[1] if mfg_name_match else None
        )

        # Address: look for line containing a 6-digit Indian PIN code or address keywords
        addr_match = None
        for line in lines:
            if re.search(r'\b[1-9][0-9]{5}\b', line):
                addr_match = line
                break
        if not addr_match:
            # Fallback search for Street/Plot/Area
            addr_m = search_patterns([
                r'(?:Address|Factory\s*Address|Mfg\s*Unit|Plot\s*No|Survey\s*No)\s*[:\.\-]?\s*(.+)',
            ])
            if addr_m:
                addr_match = addr_m[0]

        manufacturer_address = ExtractedField(
            value=addr_match,
            confidence=0.90 if addr_match else 0.0,
            sourceText=addr_match
        )

        packer_match = search_patterns([r'(?:Packed\s*by|Pkd\s*by)\s*[:\.\-]?\s*(.+)'])
        packer_name = ExtractedField(
            value=packer_match[0] if packer_match else None,
            confidence=0.89 if packer_match else 0.0,
            sourceText=packer_match[1] if packer_match else None
        )
        packer_address = ExtractedField(value=None, confidence=0.0, sourceText=None)

        importer_match = search_patterns([r'(?:Imported\s*by|Importer)\s*[:\.\-]?\s*(.+)'])
        importer_name = ExtractedField(
            value=importer_match[0] if importer_match else None,
            confidence=0.91 if importer_match else 0.0,
            sourceText=importer_match[1] if importer_match else None
        )
        importer_address = ExtractedField(value=None, confidence=0.0, sourceText=None)

        # -------------------------------------------------------------
        # 9. Dates (Rule 6(1)(d))
        # -------------------------------------------------------------
        date_patterns = [
            r'(?:Mfg\s*Date|Date\s*of\s*Mfg|Date\s*of\s*Packing|Pkd\s*Date|Manufacturing\s*Date|Packed\s*on|MFD|MFG|PKD)\s*[:\.\-]?\s*([0-9]{1,2}[\/\.-][0-9]{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\.-]*(?:20)?[12][0-9])',
            r'\b(0?[1-9]|1[0-2])[\/\.-](?:20)?(2[0-9]|1[9])\b',
        ]
        mfg_date_match = search_patterns(date_patterns)
        manufacture_date = ExtractedField(
            value=mfg_date_match[0] if mfg_date_match else None,
            confidence=0.94 if mfg_date_match else 0.0,
            sourceText=mfg_date_match[1] if mfg_date_match else None
        )
        import_date = ExtractedField(value=None, confidence=0.0, sourceText=None)

        # -------------------------------------------------------------
        # 10. Consumer Care (Rule 6(1)(da))
        # -------------------------------------------------------------
        care_name_patterns = [
            r'(?:Customer\s*Care|Consumer\s*Care|Consumer\s*Complaints|Feedback)\s*[:\-]?\s*([^,\n\r]+(?:Cell|Executive|Manager|Officer)?)',
        ]
        care_name_m = search_patterns(care_name_patterns)

        care_phone_patterns = [
            r'(?:Toll\s*Free|Phone|Tel|Helpline|Call|Contact)\s*[:\.\-]?\s*([0-9\-\+\s]{7,15})',
            r'\b(1800[-\s]?[0-9]{2,3}[-\s]?[0-9]{3,4})\b',
            r'(\+?91[-\s]?[6-9][0-9]{9})\b',
        ]
        care_phone_m = search_patterns(care_phone_patterns)

        care_email_patterns = [
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        ]
        care_email_m = search_patterns(care_email_patterns)

        consumer_care_name = ExtractedField(
            value=care_name_m[0] if care_name_m else ("Consumer Care Cell" if (care_phone_m or care_email_m) else None),
            confidence=0.90 if care_name_m else (0.80 if (care_phone_m or care_email_m) else 0.0),
            sourceText=care_name_m[1] if care_name_m else None
        )
        consumer_care_phone = ExtractedField(
            value=care_phone_m[0] if care_phone_m else None,
            confidence=0.94 if care_phone_m else 0.0,
            sourceText=care_phone_m[1] if care_phone_m else None
        )
        consumer_care_email = ExtractedField(
            value=care_email_m[0] if care_email_m else None,
            confidence=0.96 if care_email_m else 0.0,
            sourceText=care_email_m[1] if care_email_m else None
        )
        consumer_care_address = ExtractedField(
            value=addr_match if (care_name_m or care_phone_m or care_email_m) else None,
            confidence=0.85 if (care_name_m or care_phone_m or care_email_m) and addr_match else 0.0,
            sourceText=addr_match if (care_name_m or care_phone_m or care_email_m) else None
        )

        # -------------------------------------------------------------
        # 11. Country of Origin (Rule 6(1)(g))
        # -------------------------------------------------------------
        coo_patterns = [
            r'(?:Country\s*of\s*Origin|Made\s*in|Product\s*of)\s*[:\.\-]?\s*(.+)',
        ]
        coo_match = search_patterns(coo_patterns)
        coo_val = None
        coo_src = None

        if coo_match:
            coo_val = coo_match[0].split()[0] if coo_match[0] else None
            coo_src = coo_match[1]
        elif re.search(r'\b(India|Bharat)\b', full_text, re.IGNORECASE):
            coo_val = "India"
            coo_src = "India"

        country_of_origin = ExtractedField(
            value=coo_val,
            confidence=0.95 if coo_match else (0.85 if coo_val else 0.0),
            sourceText=coo_src
        )

        # -------------------------------------------------------------
        # 12. Size Dimensions (Rule 6(1)(h))
        # -------------------------------------------------------------
        size_patterns = [
            r'(?:Dimensions?|Size)\s*[:\.\-]?\s*(.+)',
        ]
        size_match = search_patterns(size_patterns)
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