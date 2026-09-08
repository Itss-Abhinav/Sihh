from fastapi import APIRouter, HTTPException
from backend.app.services.rule_engine.rules_data import LEGAL_RULES, RULEBOOK_METADATA

router = APIRouter(prefix="/api/rules", tags=["Legal Metrology Rules"])

@router.get("")
def list_rules():
    return {
        "metadata": RULEBOOK_METADATA,
        "rules": list(LEGAL_RULES.values())
    }

@router.get("/{rule_code}")
def get_rule_details(rule_code: str):
    code_upper = rule_code.upper()
    if code_upper not in LEGAL_RULES:
        raise HTTPException(status_code=404, detail="Rule not found in Rulebook 2026.2")
    return {
        "metadata": RULEBOOK_METADATA,
        "rule": LEGAL_RULES[code_upper]
    }
