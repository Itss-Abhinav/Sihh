import pytest
from backend.app.services.ocr_service import MockOcrService
from backend.app.services.extraction_service import MockLabelExtractionService
from backend.app.services.rule_engine.engine import DeterministicRuleEngine
from backend.app.schemas.rule import ExtractedLabelPayload, ExtractedField

@pytest.fixture
def setup_services():
    return MockOcrService(), MockLabelExtractionService(), DeterministicRuleEngine()

def test_demo_a_mostly_compliant(setup_services):
    ocr, extractor, engine = setup_services
    text = ocr.get_demo_text("demoA")
    payload = extractor.extract_fields(text)
    report = engine.evaluate(payload)
    
    assert report.overallStatus == "COMPLIANT"
    assert report.summary["failed"] == 0
    assert report.summary["passed"] >= 5
    # Font size, sticker, PDP should be UNABLE_TO_VERIFY
    unable_checks = [c for c in report.checks if c.status == "UNABLE_TO_VERIFY"]
    assert len(unable_checks) >= 3

def test_demo_b_missing_manufacturer(setup_services):
    ocr, extractor, engine = setup_services
    text = ocr.get_demo_text("demoB")
    payload = extractor.extract_fields(text)
    report = engine.evaluate(payload)
    
    assert report.overallStatus == "POTENTIAL_ISSUES_DETECTED"
    assert report.summary["failed"] >= 1
    failed_codes = [c.ruleCode for c in report.checks if c.status == "FAIL"]
    assert "RULE_6_1_A_MANUFACTURER" in failed_codes
    assert "RULE_6_2_CONSUMER_CARE" in failed_codes

def test_demo_c_prohibited_terms(setup_services):
    ocr, extractor, engine = setup_services
    text = ocr.get_demo_text("demoC")
    payload = extractor.extract_fields(text)
    report = engine.evaluate(payload)
    
    assert report.overallStatus == "POTENTIAL_ISSUES_DETECTED"
    failed_codes = [c.ruleCode for c in report.checks if c.status == "FAIL"]
    assert "RULE_6_1_C_NET_QUANTITY" in failed_codes  # 'approx' prohibited
    assert "RULE_THIRD_SCHEDULE" in failed_codes      # 'when packed' not allowed for body wash

def test_scope_exclusion_large_quantity(setup_services):
    _, _, engine = setup_services
    payload = ExtractedLabelPayload(
        productName=ExtractedField(value="Bulk Wheat Flour"),
        productCategory=ExtractedField(value="Food Grain"),
        netQuantity=ExtractedField(value="30 kg"),
        quantityUnit=ExtractedField(value="kg"),
        rawOcrText="Bulk Wheat Flour 30 kg for industrial supply"
    )
    report = engine.evaluate(payload)
    scope_check = next(c for c in report.checks if c.ruleCode == "RULE_3_SCOPE")
    assert scope_check.status == "NOT_APPLICABLE"

def test_small_measure_exemption(setup_services):
    _, _, engine = setup_services
    payload = ExtractedLabelPayload(
        productName=ExtractedField(value="Sample Shampoo"),
        productCategory=ExtractedField(value="Personal Care"),
        netQuantity=ExtractedField(value="6 ml"),
        quantityUnit=ExtractedField(value="ml"),
        rawOcrText="Sample Shampoo 6 ml"
    )
    report = engine.evaluate(payload)
    exempt_check = next(c for c in report.checks if c.ruleCode == "RULE_26_EXEMPTIONS")
    assert exempt_check.status == "NOT_APPLICABLE"
