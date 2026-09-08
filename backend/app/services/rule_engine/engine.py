import re
import time
from typing import List, Dict, Any, Optional
from backend.app.schemas.rule import ExtractedLabelPayload, RuleCheckResult, ComplianceReport
from backend.app.services.rule_engine.rules_data import LEGAL_RULES, RULEBOOK_METADATA
from backend.app.services.rule_engine.schedules import (
    THIRD_SCHEDULE_COMMODITIES,
    FOURTH_SCHEDULE_MAPPINGS,
    PROHIBITED_QUALIFYING_TERMS,
    PROHIBITED_COUNT_UNITS,
    VALID_SI_UNITS,
    SECOND_SCHEDULE_DATA
)

class DeterministicRuleEngine:
    def __init__(self):
        self.rules_data = LEGAL_RULES
        self.version = RULEBOOK_METADATA["version"]

    def evaluate(self, payload: ExtractedLabelPayload) -> ComplianceReport:
        start_time = time.time()
        checks: List[RuleCheckResult] = []

        raw_qty = payload.netQuantity.value or ""
        qty_num: Optional[float] = None
        qty_unit_str: Optional[str] = payload.quantityUnit.value or ""
        
        num_match = re.search(r'(\d+(?:\.\d+)?)', raw_qty)
        if num_match:
            try:
                qty_num = float(num_match.group(1))
            except ValueError:
                qty_num = None

        category_lower = (payload.productCategory.value or "").lower()
        product_lower = (payload.productName.value or "").lower()
        generic_lower = (payload.genericName.value or "").lower()
        combined_text = f"{product_lower} {generic_lower} {category_lower} {payload.rawOcrText.lower()}"

        # 1. SCOPE EXCLUSIONS — Rule 3
        is_scope_excluded = False
        scope_exclusion_reason = ""
        is_cement_or_fertilizer = any(w in combined_text for w in ["cement", "fertilizer"])
        max_qty_limit = 50.0 if is_cement_or_fertilizer else 25.0

        if qty_num and qty_unit_str in ["kg", "l", "litre", "litres"]:
            if qty_num > max_qty_limit:
                is_scope_excluded = True
                scope_exclusion_reason = f"Net quantity ({qty_num} {qty_unit_str}) exceeds retail ceiling of {max_qty_limit} {qty_unit_str} under Rule 3(a)."

        if any(w in combined_text for w in ["for industrial use only", "industrial consumer", "not for retail sale"]):
            is_scope_excluded = True
            scope_exclusion_reason = "Package designated exclusively for industrial consumer use under Rule 3(b)."

        if any(w in combined_text for w in ["institutional pack", "for institutional use only", "for hotel and hospital supply only"]):
            is_scope_excluded = True
            scope_exclusion_reason = "Package designated exclusively for institutional consumer use under Rule 3(c)."

        checks.append(RuleCheckResult(
            field="Scope Applicability",
            status="NOT_APPLICABLE" if is_scope_excluded else "PASS",
            detectedValue=f"Quantity: {raw_qty}, Category: {payload.productCategory.value}" if is_scope_excluded else "Standard Retail Package",
            expectedRequirement="Retail package governed by Legal Metrology (Packaged Commodities) Rules, 2011",
            explanation=scope_exclusion_reason if is_scope_excluded else "Package falls within standard retail consumer applicability scope of Rule 3.",
            ruleCode="RULE_3_SCOPE",
            sourceReference=LEGAL_RULES["RULE_3_SCOPE"]["reference"],
            category=LEGAL_RULES["RULE_3_SCOPE"]["category"],
            penaltyNote=LEGAL_RULES["RULE_3_SCOPE"]["penalty_note"]
        ))

        # 2. EXEMPTIONS — Rule 26
        is_exempt = False
        exemption_reason = ""
        if qty_num is not None and qty_num <= 10.0 and qty_unit_str in ["g", "ml"]:
            is_exempt = True
            exemption_reason = f"Net weight/measure ({qty_num} {qty_unit_str}) is <= 10g/10ml (Rule 26(a) small measure exemption)."
        elif any(w in combined_text for w in ["fast food", "restaurant pack", "room service"]):
            is_exempt = True
            exemption_reason = "Fast food packed by restaurant/hotel is exempt under Rule 26(b)."
        elif "bidi" in combined_text or "beedi" in combined_text:
            is_exempt = True
            exemption_reason = "Bidis are exempt from specified standard provisions under Rule 26(d)."
        elif "agarbatti" in combined_text or "incense stick" in combined_text:
            is_exempt = True
            exemption_reason = "Incense sticks carry specific regulatory exemptions under Legal Metrology."
        elif "lpg" in combined_text and "cylinder" in combined_text:
            is_exempt = True
            exemption_reason = "Domestic LPG cylinders are governed by separate Liquefied Petroleum Gas Control Orders."
        elif "formulation" in combined_text and "schedule h" in combined_text:
            is_exempt = True
            exemption_reason = "Regulated pharmaceutical drug formulation governed under Drugs and Cosmetics Act."

        checks.append(RuleCheckResult(
            field="Exemption Evaluation",
            status="NOT_APPLICABLE" if is_exempt else "PASS",
            detectedValue=f"Commodity: {payload.productName.value}, Net Qty: {raw_qty}" if is_exempt else "No Statutory Exemption Triggered",
            expectedRequirement="Check statutory exemptions under Rule 26 of LM (PC) Rules, 2011",
            explanation=exemption_reason if is_exempt else "No Rule 26 exemptions apply; full mandatory retail declarations are required.",
            ruleCode="RULE_26_EXEMPTIONS",
            sourceReference=LEGAL_RULES["RULE_26_EXEMPTIONS"]["reference"],
            category=LEGAL_RULES["RULE_26_EXEMPTIONS"]["category"],
            penaltyNote=LEGAL_RULES["RULE_26_EXEMPTIONS"]["penalty_note"]
        ))

        skip_retail_rules = is_scope_excluded or is_exempt
        # 3. MANUFACTURER / PACKER / IMPORTER DETAILS — Rule 6(1)(a) & 10(1)
        mfg_name = payload.manufacturerName.value or payload.packerName.value or payload.importerName.value
        mfg_addr = payload.manufacturerAddress.value or payload.packerAddress.value or payload.importerAddress.value

        if skip_retail_rules:
            mfg_status = "NOT_APPLICABLE"
            mfg_exp = "Retail declaration exempt under scope/Rule 26."
        elif mfg_name and mfg_addr:
            addr_lower = mfg_addr.lower()
            has_pin = bool(re.search(r'\b\d{6}\b', mfg_addr))
            has_geo = any(term in addr_lower for term in ["road", "street", "plot", "survey", "sector", "industrial", "phase", "city", "state", "kerala", "karnataka", "delhi", "maharashtra", "gujarat", "tamil nadu", "bengaluru", "kochi", "mumbai"])
            if has_pin or has_geo or len(mfg_addr.split()) >= 3:
                mfg_status = "PASS"
                mfg_exp = f"Valid manufacturer identity ('{mfg_name}') and complete postal address detected under Rule 6(1)(a) and Rule 10(1)."
            else:
                mfg_status = "REQUIRES_VERIFICATION"
                mfg_exp = f"Address detected ('{mfg_addr}') appears abbreviated; verify whether registered shorter-address exemption applies under Rule 10(1) proviso."
        elif mfg_name and not mfg_addr:
            mfg_status = "FAIL"
            mfg_exp = "Manufacturer name detected but physical premises address is missing. Rule 10(1) mandates complete factory/office address."
        else:
            mfg_status = "FAIL"
            mfg_exp = "Name and address of manufacturer/packer/importer is missing from label declarations. Required by Rule 6(1)(a)."

        checks.append(RuleCheckResult(
            field="Manufacturer / Packer Details",
            status=mfg_status,
            detectedValue=f"{mfg_name or 'Not detected'} | {mfg_addr or 'No address'}",
            expectedRequirement="Name and complete physical/postal address of manufacturer, packer, or importer",
            explanation=mfg_exp,
            ruleCode="RULE_6_1_A_MANUFACTURER",
            sourceReference=LEGAL_RULES["RULE_6_1_A_MANUFACTURER"]["reference"],
            category=LEGAL_RULES["RULE_6_1_A_MANUFACTURER"]["category"],
            penaltyNote=LEGAL_RULES["RULE_6_1_A_MANUFACTURER"]["penalty_note"]
        ))

        # 4. GENERIC NAME — Rule 6(1)(b)
        generic_val = payload.genericName.value
        if skip_retail_rules:
            gen_status = "NOT_APPLICABLE"
            gen_exp = "Exempt from retail declarations."
        elif generic_val and len(generic_val.strip()) > 1:
            gen_status = "PASS"
            gen_exp = f"Generic/common commodity name declared as '{generic_val}' conforming to Rule 6(1)(b)."
        elif payload.productName.value and not any(w in payload.productName.value.lower() for w in ["generic", "item", "product"]):
            gen_status = "REQUIRES_VERIFICATION"
            gen_exp = f"Specific generic name field not isolated, but product title contains descriptive term '{payload.productName.value}'. Verify clear prominence."
        else:
            gen_status = "FAIL"
            gen_exp = "Common or generic name of the commodity is missing. Mandatory under Rule 6(1)(b)."

        checks.append(RuleCheckResult(
            field="Generic Commodity Name",
            status=gen_status,
            detectedValue=generic_val or payload.productName.value,
            expectedRequirement="Common or generic name of the packaged commodity",
            explanation=gen_exp,
            ruleCode="RULE_6_1_B_GENERIC_NAME",
            sourceReference=LEGAL_RULES["RULE_6_1_B_GENERIC_NAME"]["reference"],
            category=LEGAL_RULES["RULE_6_1_B_GENERIC_NAME"]["category"],
            penaltyNote=LEGAL_RULES["RULE_6_1_B_GENERIC_NAME"]["penalty_note"]
        ))

        # 5. NET QUANTITY — Rule 6(1)(c) & Rules 11-13
        net_qty_val = payload.netQuantity.value
        if skip_retail_rules:
            qty_status = "NOT_APPLICABLE"
            qty_exp = "Quantity rules exempt under Rule 3 / Rule 26."
        elif not net_qty_val:
            qty_status = "FAIL"
            qty_exp = "Net quantity declaration is missing. Mandatory under Rule 6(1)(c)."
        else:
            net_lower = net_qty_val.lower()
            found_prohibited_terms = [t for t in PROHIBITED_QUALIFYING_TERMS if re.search(r'\b' + re.escape(t) + r'\b', net_lower)]
            found_prohibited_counts = [c for c in PROHIBITED_COUNT_UNITS if re.search(r'\b' + re.escape(c) + r'\b', net_lower)]
            unit_matched = False
            for u in VALID_SI_UNITS:
                if re.search(r'\b' + re.escape(u) + r'\b', net_lower):
                    unit_matched = True
                    break

            if found_prohibited_terms:
                qty_status = "FAIL"
                qty_exp = f"Prohibited qualifying expression detected: '{', '.join(found_prohibited_terms)}'. Rule 13 prohibits qualifying words like 'approx', 'minimum', etc."
            elif found_prohibited_counts:
                qty_status = "FAIL"
                qty_exp = f"Prohibited non-standard count unit detected: '{', '.join(found_prohibited_counts)}'. Rule 13(5) prohibits expressions like dozen, score, gross."
            elif not unit_matched:
                qty_status = "FAIL"
                qty_exp = f"Quantity '{net_qty_val}' does not declare a recognized SI unit (g, kg, ml, l, cm, m, N, U). Mandatory under Rule 11 & 12."
            else:
                if qty_num and qty_num >= 1000.0 and qty_unit_str == "g":
                    qty_status = "REQUIRES_VERIFICATION"
                    qty_exp = f"Declared quantity is {qty_num} g. Under Rule 12, quantities of 1000g or more should generally be expressed in kg."
                elif qty_num and qty_num >= 1000.0 and qty_unit_str == "ml":
                    qty_status = "REQUIRES_VERIFICATION"
                    qty_exp = f"Declared quantity is {qty_num} ml. Under Rule 12, quantities of 1000ml or more should generally be expressed in L."
                else:
                    qty_status = "PASS"
                    qty_exp = f"Net quantity declared in valid SI units ({net_qty_val}) without prohibited qualifying expressions."

        checks.append(RuleCheckResult(
            field="Net Quantity & Units",
            status=qty_status,
            detectedValue=net_qty_val,
            expectedRequirement="Net quantity declared in standard SI units (g, kg, ml, l, N, etc.) with no prohibited qualifiers",
            explanation=qty_exp,
            ruleCode="RULE_6_1_C_NET_QUANTITY",
            sourceReference=LEGAL_RULES["RULE_6_1_C_NET_QUANTITY"]["reference"],
            category=LEGAL_RULES["RULE_6_1_C_NET_QUANTITY"]["category"],
            penaltyNote=LEGAL_RULES["RULE_6_1_C_NET_QUANTITY"]["penalty_note"]
        ))

        # 6. THIRD SCHEDULE ('WHEN PACKED')
        raw_text_lower = payload.rawOcrText.lower()
        has_when_packed = "when packed" in raw_text_lower
        if has_when_packed:
            is_third_sched_allowed = any(c in combined_text for c in THIRD_SCHEDULE_COMMODITIES)
            if is_third_sched_allowed:
                wp_status = "PASS"
                wp_exp = "'When packed' declaration is validly used for permitted Third Schedule commodity (soap, lotion, or cream)."
            else:
                wp_status = "FAIL"
                wp_exp = "'When packed' declaration detected on non-permitted commodity. Third Schedule restricts 'when packed' exclusively to soaps, lotions, and creams."
        else:
            wp_status = "PASS"
            wp_exp = "No prohibited 'when packed' expression detected on net quantity declaration."

        checks.append(RuleCheckResult(
            field="Third Schedule ('When Packed')",
            status=wp_status,
            detectedValue="'when packed' detected" if has_when_packed else "Standard Net Quantity",
            expectedRequirement="'When packed' permitted solely for soaps, lotions, and non-milk creams under Third Schedule",
            explanation=wp_exp,
            ruleCode="RULE_THIRD_SCHEDULE",
            sourceReference=LEGAL_RULES["RULE_THIRD_SCHEDULE"]["reference"],
            category=LEGAL_RULES["RULE_THIRD_SCHEDULE"]["category"],
            penaltyNote=LEGAL_RULES["RULE_THIRD_SCHEDULE"]["penalty_note"]
        ))

        # 7. FOURTH SCHEDULE
        fourth_sched_status = "PASS"
        fourth_sched_exp = "Unit aligns with standard commodity schedules or general SI provisions."
        for comm_key, mandated_unit in FOURTH_SCHEDULE_MAPPINGS.items():
            clean_key = comm_key.replace("_", " ")
            if clean_key in combined_text:
                if mandated_unit == "weight" and qty_unit_str not in ["g", "kg"]:
                    fourth_sched_status = "FAIL"
                    fourth_sched_exp = f"Fourth Schedule mandates '{clean_key}' must be declared by weight (g/kg). Detected unit: '{qty_unit_str}'."
                elif mandated_unit == "volume" and qty_unit_str not in ["ml", "l", "litre", "litres"]:
                    fourth_sched_status = "FAIL"
                    fourth_sched_exp = f"Fourth Schedule mandates '{clean_key}' must be declared by volume (ml/L). Detected unit: '{qty_unit_str}'."
                elif mandated_unit == "number" and qty_unit_str not in ["n", "u", "units", "unit"]:
                    fourth_sched_status = "FAIL"
                    fourth_sched_exp = f"Fourth Schedule mandates '{clean_key}' must be declared by number (N/U). Detected unit: '{qty_unit_str}'."
                else:
                    fourth_sched_status = "PASS"
                    fourth_sched_exp = f"Declared unit '{qty_unit_str}' complies with Fourth Schedule mandate for {clean_key}."
                break

        checks.append(RuleCheckResult(
            field="Fourth Schedule Commodity Units",
            status=fourth_sched_status,
            detectedValue=f"{payload.productCategory.value}: {raw_qty}",
            expectedRequirement="Prescribed units of measure for specific Fourth Schedule commodities",
            explanation=fourth_sched_exp,
            ruleCode="RULE_FOURTH_SCHEDULE",
            sourceReference=LEGAL_RULES["RULE_FOURTH_SCHEDULE"]["reference"],
            category=LEGAL_RULES["RULE_FOURTH_SCHEDULE"]["category"],
            penaltyNote=LEGAL_RULES["RULE_FOURTH_SCHEDULE"]["penalty_note"]
        ))

        # 8. MANUFACTURE DATE — Rule 6(1)(d)
        mfg_date_val = payload.manufactureDate.value
        if skip_retail_rules:
            date_status = "NOT_APPLICABLE"
            date_exp = "Date rules exempt under scope/Rule 26."
        elif not mfg_date_val:
            date_status = "FAIL"
            date_exp = "Date of manufacture, packing, or import is missing. Mandatory under Rule 6(1)(d)."
        else:
            has_month_year = bool(re.search(r'(?:\d{1,2}[\/\-\.]\d{4}|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{4}\b|\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', mfg_date_val, re.IGNORECASE))
            if has_month_year:
                date_status = "PASS"
                date_exp = f"Date of manufacture declared in recognized format ('{mfg_date_val}') satisfying Rule 6(1)(d)."
            else:
                date_status = "FAIL"
                date_exp = f"Date '{mfg_date_val}' does not specify valid month and year (MM/YYYY). Rule 6(1)(d) mandates month and year."

        checks.append(RuleCheckResult(
            field="Date of Manufacture / Packing",
            status=date_status,
            detectedValue=mfg_date_val,
            expectedRequirement="Month and year of manufacture, packing, or import (MM/YYYY)",
            explanation=date_exp,
            ruleCode="RULE_6_1_D_MFG_DATE",
            sourceReference=LEGAL_RULES["RULE_6_1_D_MFG_DATE"]["reference"],
            category=LEGAL_RULES["RULE_6_1_D_MFG_DATE"]["category"],
            penaltyNote=LEGAL_RULES["RULE_6_1_D_MFG_DATE"]["penalty_note"]
        ))
        # 9. MRP — Rule 6(1)(e) & Rule 2(m)
        mrp_val = payload.mrp.value
        if skip_retail_rules:
            mrp_status = "NOT_APPLICABLE"
            mrp_exp = "Pricing declaration exempt under scope/Rule 26."
        elif not mrp_val:
            mrp_status = "FAIL"
            mrp_exp = "Maximum Retail Price (MRP) declaration is missing. Mandatory under Rule 6(1)(e)."
        else:
            mrp_lower = (mrp_val + " " + raw_text_lower).lower()
            has_prefix = any(p in mrp_lower for p in ["mrp", "maximum retail price", "max. retail price", "max retail price"])
            has_tax_phrase = any(t in mrp_lower for t in ["inclusive of all taxes", "incl. of all taxes", "incl of all taxes", "incl. all taxes", "incl all taxes"])
            has_price_num = bool(re.search(r'\d+', mrp_val))

            if not has_price_num:
                mrp_status = "FAIL"
                mrp_exp = "MRP declaration found without valid numeric monetary figure."
            elif not has_prefix:
                mrp_status = "FAIL"
                mrp_exp = f"Price declared as '{mrp_val}' but lacks statutory prefix 'MRP' or 'Maximum Retail Price' under Rule 6(1)(e)."
            elif not has_tax_phrase:
                mrp_status = "FAIL"
                mrp_exp = f"MRP declared as '{mrp_val}' but missing mandatory phrase 'inclusive of all taxes' (or 'incl. of all taxes') under Rule 6(1)(e)."
            else:
                mrp_status = "PASS"
                mrp_exp = f"MRP clearly declared with recognized prefix and 'inclusive of all taxes' phrase ('{mrp_val}')."

        checks.append(RuleCheckResult(
            field="Maximum Retail Price (MRP)",
            status=mrp_status,
            detectedValue=mrp_val,
            expectedRequirement="MRP with recognized prefix and mandatory 'inclusive of all taxes' phrase",
            explanation=mrp_exp,
            ruleCode="RULE_6_1_E_MRP",
            sourceReference=LEGAL_RULES["RULE_6_1_E_MRP"]["reference"],
            category=LEGAL_RULES["RULE_6_1_E_MRP"]["category"],
            penaltyNote=LEGAL_RULES["RULE_6_1_E_MRP"]["penalty_note"]
        ))

        # 10. UNIT SALE PRICE — Rule 6(1)(r)
        usp_val = payload.unitSalePrice.value
        if skip_retail_rules:
            usp_status = "NOT_APPLICABLE"
            usp_exp = "Exempt under Rule 3 / Rule 26."
        elif usp_val:
            usp_status = "PASS"
            usp_exp = f"Unit Sale Price declared as '{usp_val}' in accordance with amended Rule 6(1)(r)."
        else:
            usp_status = "REQUIRES_VERIFICATION"
            usp_exp = "Unit Sale Price (USP) was not isolated from label image. Rule 6(1)(r) mandates unit price per g/ml or kg/L unless specifically exempt."

        checks.append(RuleCheckResult(
            field="Unit Sale Price (USP)",
            status=usp_status,
            detectedValue=usp_val or "Not isolated",
            expectedRequirement="Unit sale price per g/ml (for <=1kg/1L) or per kg/L (for >1kg/1L)",
            explanation=usp_exp,
            ruleCode="RULE_6_1_R_UNIT_SALE_PRICE",
            sourceReference=LEGAL_RULES["RULE_6_1_R_UNIT_SALE_PRICE"]["reference"],
            category=LEGAL_RULES["RULE_6_1_R_UNIT_SALE_PRICE"]["category"],
            penaltyNote=LEGAL_RULES["RULE_6_1_R_UNIT_SALE_PRICE"]["penalty_note"]
        ))

        # 11. CONSUMER CARE — Rule 6(2)
        care_name = payload.consumerCareName.value
        care_phone = payload.consumerCarePhone.value
        care_email = payload.consumerCareEmail.value
        care_addr = payload.consumerCareAddress.value

        if skip_retail_rules:
            care_status = "NOT_APPLICABLE"
            care_exp = "Exempt under Rule 3 / Rule 26."
        else:
            detected_elements = []
            if care_name: detected_elements.append("Contact/Office Name")
            if care_phone: detected_elements.append(f"Phone: {care_phone}")
            if care_email: detected_elements.append(f"Email: {care_email}")
            if care_addr: detected_elements.append("Address")

            if care_phone and (care_email or care_addr):
                care_status = "PASS"
                care_exp = f"Consumer redressal contact verified with phone and digital/postal redressal channels: {', '.join(detected_elements)}."
            elif care_phone and not care_email and not care_addr:
                care_status = "REQUIRES_VERIFICATION"
                care_exp = f"Helpline telephone detected ('{care_phone}'), but specific postal contact address or email was not clearly identified under Rule 6(2)."
            else:
                care_status = "FAIL"
                care_exp = "Consumer care contact details (name, phone, address, and email) are missing. Mandatory under Rule 6(2)."

        checks.append(RuleCheckResult(
            field="Consumer Care Redressal",
            status=care_status,
            detectedValue=f"Phone: {care_phone or 'None'}, Email: {care_email or 'None'}, Contact: {care_name or 'None'}",
            expectedRequirement="Name, address, phone number, and email of consumer grievance officer",
            explanation=care_exp,
            ruleCode="RULE_6_2_CONSUMER_CARE",
            sourceReference=LEGAL_RULES["RULE_6_2_CONSUMER_CARE"]["reference"],
            category=LEGAL_RULES["RULE_6_2_CONSUMER_CARE"]["category"],
            penaltyNote=LEGAL_RULES["RULE_6_2_CONSUMER_CARE"]["penalty_note"]
        ))

        # 12. COUNTRY OF ORIGIN — Rule 6(1)(n)
        origin_val = payload.countryOfOrigin.value
        is_imported = bool(payload.importerName.value or "imported" in combined_text)

        if skip_retail_rules:
            coo_status = "NOT_APPLICABLE"
            coo_exp = "Exempt under Rule 3 / Rule 26."
        elif is_imported:
            if origin_val:
                coo_status = "PASS"
                coo_exp = f"Country of origin declared as '{origin_val}' for imported commodity under Rule 6(1)(n)."
            else:
                coo_status = "FAIL"
                coo_exp = "Package appears to be imported, but Country of Origin is not declared. Mandatory under Rule 6(1)(n)."
        else:
            if origin_val:
                coo_status = "PASS"
                coo_exp = f"Country of origin declared as '{origin_val}'."
            else:
                coo_status = "PASS"
                coo_exp = "Domestic package: manufacturer located in India; separate import declaration not triggered."

        checks.append(RuleCheckResult(
            field="Country of Origin",
            status=coo_status,
            detectedValue=origin_val or ("Domestic (India)" if mfg_addr and "india" in mfg_addr.lower() else "Not isolated"),
            expectedRequirement="Mandatory declaration of country of origin for imported goods under Rule 6(1)(n)",
            explanation=coo_exp,
            ruleCode="RULE_6_1_N_COUNTRY_OF_ORIGIN",
            sourceReference=LEGAL_RULES["RULE_6_1_N_COUNTRY_OF_ORIGIN"]["reference"],
            category=LEGAL_RULES["RULE_6_1_N_COUNTRY_OF_ORIGIN"]["category"],
            penaltyNote=LEGAL_RULES["RULE_6_1_N_COUNTRY_OF_ORIGIN"]["penalty_note"]
        ))

        # 13. SIZE & DIMENSIONS — Rule 6(1)(f)
        dims_val = payload.sizeDimensions.value
        requires_dims = any(w in combined_text for w in ["garment", "shirt", "trousers", "bedsheet", "tile", "towel", "cloth", "fabric", "paper"])

        if skip_retail_rules:
            dim_status = "NOT_APPLICABLE"
            dim_exp = "Exempt under Rule 3 / Rule 26."
        elif requires_dims:
            if dims_val:
                dim_status = "PASS"
                dim_exp = f"Dimensions declared as '{dims_val}' for size-dependent commodity under Rule 6(1)(f)."
            else:
                dim_status = "FAIL"
                dim_exp = "Size/dimensions are mandatory for this commodity category under Rule 6(1)(f) but were not detected."
        else:
            dim_status = "NOT_APPLICABLE"
            dim_exp = "Package commodity category does not mandate physical size/dimensions declaration."

        checks.append(RuleCheckResult(
            field="Dimensions / Size Declarations",
            status=dim_status,
            detectedValue=dims_val or "N/A for this commodity",
            expectedRequirement="Dimensions required for garments, textiles, tiles, and dimensional goods under Rule 6(1)(f)",
            explanation=dim_exp,
            ruleCode="RULE_6_1_F_DIMENSIONS",
            sourceReference=LEGAL_RULES["RULE_6_1_F_DIMENSIONS"]["reference"],
            category=LEGAL_RULES["RULE_6_1_F_DIMENSIONS"]["category"],
            penaltyNote=LEGAL_RULES["RULE_6_1_F_DIMENSIONS"]["penalty_note"]
        ))
        # 14. STICKER CHECK — Rule 6(3) & 6(4)
        checks.append(RuleCheckResult(
            field="Label Sticker & Tamper Verification",
            status="UNABLE_TO_VERIFY",
            detectedValue="2D Optical Capture",
            expectedRequirement="Prohibition of unauthorized stickers or altered declarations under Rule 6(3) and 6(4)",
            explanation="Automated screening limitation: A single 2D photograph cannot reliably determine physical sticker adhesive or permitted regulatory sticker exemptions. Requires manual physical inspection.",
            ruleCode="RULE_6_3_4_STICKER_CHECK",
            sourceReference=LEGAL_RULES["RULE_6_3_4_STICKER_CHECK"]["reference"],
            category=LEGAL_RULES["RULE_6_3_4_STICKER_CHECK"]["category"],
            penaltyNote=LEGAL_RULES["RULE_6_3_4_STICKER_CHECK"]["penalty_note"]
        ))

        # 15. FONT SIZE — Rule 7
        checks.append(RuleCheckResult(
            field="Statutory Font Height (mm)",
            status="UNABLE_TO_VERIFY",
            detectedValue="Pixel Resolution (Non-calibrated)",
            expectedRequirement="Minimum numeral/letter height in millimeters (1.0mm - 4.0mm) under Rule 7 Table I",
            explanation="Optical analysis limitation: Digital camera images cannot measure absolute physical millimeters without reference millimeter calibration scales on the package surface.",
            ruleCode="RULE_7_FONT_SIZE",
            sourceReference=LEGAL_RULES["RULE_7_FONT_SIZE"]["reference"],
            category=LEGAL_RULES["RULE_7_FONT_SIZE"]["category"],
            penaltyNote=LEGAL_RULES["RULE_7_FONT_SIZE"]["penalty_note"]
        ))

        # 16. PDP — Rule 8
        checks.append(RuleCheckResult(
            field="Principal Display Panel (PDP) Ratio",
            status="UNABLE_TO_VERIFY",
            detectedValue="2D Label Crop",
            expectedRequirement="PDP area must equal at least 40% of package face under Rule 8",
            explanation="Geometric limitation: 3D package dimensions and full cylindrical/rectangular surface area cannot be calculated from a single face photo.",
            ruleCode="RULE_8_PDP",
            sourceReference=LEGAL_RULES["RULE_8_PDP"]["reference"],
            category=LEGAL_RULES["RULE_8_PDP"]["category"],
            penaltyNote=LEGAL_RULES["RULE_8_PDP"]["penalty_note"]
        ))

        # 17. MANNER OF DECLARATION — Rule 9
        has_devanagari = bool(re.search(r'[\u0900-\u097F]', payload.rawOcrText))
        has_english = bool(re.search(r'[A-Za-z]{3,}', payload.rawOcrText))

        if has_devanagari or has_english:
            lang_status = "PASS"
            lang_detected = "English and Hindi (Devanagari)" if (has_devanagari and has_english) else ("English" if has_english else "Hindi (Devanagari)")
            lang_exp = f"Declarations presented in authorized language ({lang_detected}) conforming to Rule 9."
        else:
            lang_status = "FAIL"
            lang_detected = "Unrecognized"
            lang_exp = "Declarations must be conspicuous and in either Hindi (Devanagari script) or English under Rule 9."

        checks.append(RuleCheckResult(
            field="Manner of Declaration & Language",
            status=lang_status,
            detectedValue=lang_detected,
            expectedRequirement="Declarations in Hindi (Devanagari) or English with clear legibility and prominence",
            explanation=lang_exp,
            ruleCode="RULE_9_MANNER_OF_DECLARATION",
            sourceReference=LEGAL_RULES["RULE_9_MANNER_OF_DECLARATION"]["reference"],
            category=LEGAL_RULES["RULE_9_MANNER_OF_DECLARATION"]["category"],
            penaltyNote=LEGAL_RULES["RULE_9_MANNER_OF_DECLARATION"]["penalty_note"]
        ))

        # 18. SECOND SCHEDULE
        matched_sched_commodity = None
        for item_name in SECOND_SCHEDULE_DATA.keys():
            if item_name in combined_text:
                matched_sched_commodity = item_name
                break

        if matched_sched_commodity:
            allowed_sizes = SECOND_SCHEDULE_DATA[matched_sched_commodity]
            clean_q = (raw_qty or "").lower().replace(" ", "")
            if any(s in clean_q for s in allowed_sizes):
                sec_status = "PASS"
                sec_exp = f"Declared quantity matches prescribed Second Schedule standard pack size for {matched_sched_commodity}."
            else:
                sec_status = "REQUIRES_VERIFICATION"
                sec_exp = f"Package size '{raw_qty}' is outside historical Second Schedule standard sizes ({', '.join(allowed_sizes[:4])}...). Requires verification against recent deregulation notifications (valid if Unit Sale Price is declared)."
        else:
            sec_status = "NOT_APPLICABLE"
            sec_exp = "Commodity is not listed under Second Schedule standard sizing mandates."

        checks.append(RuleCheckResult(
            field="Second Schedule Standard Pack Sizes",
            status=sec_status,
            detectedValue=raw_qty or "N/A",
            expectedRequirement="Prescribed standard package quantities under Second Schedule",
            explanation=sec_exp,
            ruleCode="RULE_SECOND_SCHEDULE",
            sourceReference=LEGAL_RULES["RULE_SECOND_SCHEDULE"]["reference"],
            category=LEGAL_RULES["RULE_SECOND_SCHEDULE"]["category"],
            penaltyNote=LEGAL_RULES["RULE_SECOND_SCHEDULE"]["penalty_note"]
        ))

        # 19. WHOLESALE PACKAGES — Rule 24
        checks.append(RuleCheckResult(
            field="Wholesale Package Compliance",
            status="NOT_APPLICABLE",
            detectedValue="Individual Retail Scan",
            expectedRequirement="Rule 24 applies to wholesale packages intended for intermediate sale to retailers",
            explanation="Package is evaluated as an individual consumer retail unit; Rule 24 wholesale declarations do not apply.",
            ruleCode="RULE_24_WHOLESALE",
            sourceReference=LEGAL_RULES["RULE_24_WHOLESALE"]["reference"],
            category=LEGAL_RULES["RULE_24_WHOLESALE"]["category"],
            penaltyNote=LEGAL_RULES["RULE_24_WHOLESALE"]["penalty_note"]
        ))

        # 20. OUT OF SCOPE / PHYSICAL
        checks.append(RuleCheckResult(
            field="Physical Testing & Gravimetric Verification",
            status="UNABLE_TO_VERIFY",
            detectedValue="Image Screening Only",
            expectedRequirement="Physical weighing and Maximum Permissible Error (MPE) tolerances",
            explanation="Out of scope for image analysis: Physical mass, tare weight, laboratory sampling, and weighing machine certification cannot be verified from a digital image.",
            ruleCode="OUT_OF_SCOPE_PHYSICAL",
            sourceReference=LEGAL_RULES["OUT_OF_SCOPE_PHYSICAL"]["reference"],
            category=LEGAL_RULES["OUT_OF_SCOPE_PHYSICAL"]["category"],
            penaltyNote=LEGAL_RULES["OUT_OF_SCOPE_PHYSICAL"]["penalty_note"]
        ))

        # 21. E-COMMERCE RULE
        checks.append(RuleCheckResult(
            field="E-Commerce Marketplace Declarations",
            status="NOT_APPLICABLE",
            detectedValue="Physical Package Label",
            expectedRequirement="Mandatory digital platform declarations under Rule 6(10) on e-commerce catalog pages",
            explanation="Platform-level requirement: Digital marketplace filtering, search attributes, and web display are out of scope for physical commodity label scanning.",
            ruleCode="RULE_ECOMMERCE_2026",
            sourceReference=LEGAL_RULES["RULE_ECOMMERCE_2026"]["reference"],
            category=LEGAL_RULES["RULE_ECOMMERCE_2026"]["category"],
            penaltyNote=LEGAL_RULES["RULE_ECOMMERCE_2026"]["penalty_note"]
        ))

        # SUMMARY
        summary = {
            "total": len(checks),
            "passed": sum(1 for c in checks if c.status == "PASS"),
            "failed": sum(1 for c in checks if c.status == "FAIL"),
            "requires_verification": sum(1 for c in checks if c.status == "REQUIRES_VERIFICATION"),
            "unable_to_verify": sum(1 for c in checks if c.status == "UNABLE_TO_VERIFY"),
            "not_applicable": sum(1 for c in checks if c.status == "NOT_APPLICABLE")
        }

        if summary["failed"] > 0:
            overall_status = "POTENTIAL_ISSUES_DETECTED"
        elif summary["passed"] >= 4 and summary["failed"] == 0:
            overall_status = "COMPLIANT"
        elif summary["requires_verification"] > 0:
            overall_status = "PARTIALLY_VERIFIED"
        else:
            overall_status = "UNABLE_TO_VERIFY"

        exec_time = round((time.time() - start_time) * 1000, 2)

        return ComplianceReport(
            overallStatus=overall_status,
            disclaimer=RULEBOOK_METADATA["disclaimer"],
            summary=summary,
            checks=checks,
            extractedData=payload.model_dump(),
            rawOcrText=payload.rawOcrText,
            executionTimeMs=exec_time
        )
