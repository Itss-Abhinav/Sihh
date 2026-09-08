import pytest
from backend.app.services.extraction_service import MockLabelExtractionService, normalize_mrp
from backend.app.services.rule_engine.engine import DeterministicRuleEngine

def test_britannia_good_day_extraction():
    service = MockLabelExtractionService()
    engine = DeterministicRuleEngine()

    raw_text = """
    BRITANNIA
    GOOD DAY BUTTER COOKIES
    Generic Name: Butter Cookies
    Category: Food & Confectionery
    Net Quantity: 200 g
    MRP: Rs. 45.00 (inclusive of all taxes)
    Unit Sale Price: Rs. 0.225 / g
    Mfg Date: 08/2026
    Manufactured and Packed by: Britannia Industries Ltd.
    Address: Plot 42, KIADB Industrial Area, Phase 2, Whitefield, Bengaluru, Karnataka - 560066
    Customer Care: Consumer Care Manager, Britannia Industries Ltd.
    Toll Free: 1800-425-4449
    Email: feedback@britannia.co.in
    Country of Origin: India
    """

    extracted = service.extract_fields(raw_text, category_hint="Food & Confectionery")

    assert extracted.genericName.value == "Butter Cookies"
    assert extracted.brandName.value == "BRITANNIA"
    assert "45.00" in (extracted.mrp.value or "")
    assert extracted.netQuantity.value == "200 g"
    assert extracted.quantityUnit.value == "g"
    assert extracted.manufactureDate.value == "08/2026"
    assert "Britannia" in (extracted.manufacturerName.value or "")
    assert "560066" in (extracted.manufacturerAddress.value or "")
    assert "1800-425-4449" in (extracted.consumerCarePhone.value or "")
    assert extracted.countryOfOrigin.value == "India"

    report = engine.evaluate(extracted)
    assert report.summary["total"] == 21
    code_map = {c.ruleCode: c.status for c in report.checks}
    assert code_map["RULE_6_1_E_MRP"] == "PASS"
    assert code_map["RULE_6_1_C_NET_QUANTITY"] == "PASS"
    assert code_map["RULE_6_1_B_GENERIC_NAME"] == "PASS"
    assert code_map["RULE_6_1_D_MFG_DATE"] == "PASS"
    assert code_map["RULE_6_1_A_MANUFACTURER"] == "PASS"
    assert code_map["RULE_6_2_CONSUMER_CARE"] == "PASS"
    assert code_map["RULE_6_1_N_COUNTRY_OF_ORIGIN"] == "PASS"

def test_parle_g_extraction():
    service = MockLabelExtractionService()
    engine = DeterministicRuleEngine()

    raw_text = """
    PARLE-G
    ORIGINAL GLUCO BISCUITS
    Net Weight: 250 g
    MRP: Rs. 25.00 (INCL. OF ALL TAXES)
    Unit Sale Price: Rs. 0.10/g
    Mfg: 06/2026
    Mfd by: Parle Products Pvt. Ltd.
    North Level Crossing, Vile Parle East, Mumbai 400057
    Toll Free: 1800-22-2229
    Email: cs@parle.biz
    Country of Origin: India
    """

    extracted = service.extract_fields(raw_text, category_hint="Food & Confectionery")

    assert "BISCUITS" in (extracted.genericName.value or "").upper()
    assert "PARLE" in (extracted.brandName.value or "").upper()
    assert "25.00" in (extracted.mrp.value or "")
    assert extracted.netQuantity.value == "250 g"
    assert extracted.quantityUnit.value == "g"
    assert "Parle Products" in (extracted.manufacturerName.value or "")
    assert "400057" in (extracted.manufacturerAddress.value or "")
    assert extracted.countryOfOrigin.value == "India"

    report = engine.evaluate(extracted)
    code_map = {c.ruleCode: c.status for c in report.checks}
    assert code_map["RULE_6_1_E_MRP"] == "PASS"
    assert code_map["RULE_6_1_C_NET_QUANTITY"] == "PASS"

def test_rejection_of_ocr_noise():
    service = MockLabelExtractionService()

    # Verify "n 9" is rejected and never falsely matched as MRP
    extracted_noise = service.extract_fields("n 9")
    assert extracted_noise.mrp.value is None
    assert extracted_noise.mrp.confidence == 0.0
    assert extracted_noise.genericName.value is None
    assert extracted_noise.netQuantity.value is None

    # Verify "IR," is rejected
    extracted_ir = service.extract_fields("IR,")
    assert extracted_ir.mrp.value is None
    assert extracted_ir.mrp.confidence == 0.0
