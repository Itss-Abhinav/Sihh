from typing import Dict, Any

RULEBOOK_METADATA: Dict[str, Any] = {
    "version": "2026.2",
    "title": "The Legal Metrology (Packaged Commodities) Rules, 2011 & Amendments",
    "authority": "Ministry of Consumer Affairs, Food and Public Distribution, Government of India",
    "disclaimer": "Automated screening result — not a legal determination. Rules represented reflect development rulebook 2026.2.",
    "jurisdiction": "India"
}

LEGAL_RULES: Dict[str, Dict[str, Any]] = {
    "RULE_3_SCOPE": {
        "rule_code": "RULE_3_SCOPE",
        "name": "Scope & Applicability Exclusions",
        "category": "Scope & Exemptions",
        "reference": "Rule 3, Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "Retail package requirements do not apply to packages >25kg or 25L (except cement/fertilizer up to 50kg), or packages meant solely for industrial or institutional consumers.",
        "penalty_note": "Non-applicable scopes are excluded from retail compliance screening."
    },
    "RULE_26_EXEMPTIONS": {
        "rule_code": "RULE_26_EXEMPTIONS",
        "name": "Small Measure & Specialized Exemptions",
        "category": "Scope & Exemptions",
        "reference": "Rule 26, Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "Exempts packages <=10g or 10ml, fast food packed by hotels/restaurants, agricultural produce >50kg, bidis, domestic LPG, and regimes governed by specific Drugs/Cosmetics/Seeds rules.",
        "penalty_note": "Exempt commodities are not subject to standard retail declaration penalties."
    },
    "RULE_6_1_A_MANUFACTURER": {
        "rule_code": "RULE_6_1_A_MANUFACTURER",
        "name": "Manufacturer / Packer / Importer Identity & Complete Address",
        "category": "Mandatory Declarations",
        "reference": "Rule 6(1)(a) & Rule 10(1), Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "Every package must bear the name and complete address of the manufacturer, or packer, or importer.",
        "penalty_note": "Section 36(1) of Legal Metrology Act, 2009: Fine up to ₹25,000 for first offence, ₹50,000 for second, and up to ₹1,00,000 or imprisonment for subsequent offences."
    },
    "RULE_6_1_B_GENERIC_NAME": {
        "rule_code": "RULE_6_1_B_GENERIC_NAME",
        "name": "Generic or Common Commodity Name",
        "category": "Mandatory Declarations",
        "reference": "Rule 6(1)(b), Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "The common or generic names of the commodity contained in the package must be clearly stated.",
        "penalty_note": "Section 36(1) of Legal Metrology Act, 2009 for missing mandatory declarations."
    },
    "RULE_6_1_C_NET_QUANTITY": {
        "rule_code": "RULE_6_1_C_NET_QUANTITY",
        "name": "Net Quantity Declaration & Standard SI Units",
        "category": "Quantity & Measurement",
        "reference": "Rule 6(1)(c) & Rules 11-13, Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "Net quantity must be declared in standard SI units (g, kg, ml, l, m, N, etc.) without misleading qualifying expressions (approx, minimum, etc.).",
        "penalty_note": "Section 36(1) & Section 36(2) for non-standard units or misleading quantity statements."
    },
    "RULE_6_1_D_MFG_DATE": {
        "rule_code": "RULE_6_1_D_MFG_DATE",
        "name": "Date of Manufacture, Packing or Import",
        "category": "Mandatory Declarations",
        "reference": "Rule 6(1)(d), Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "Month and year in which the commodity is manufactured, pre-packed, or imported (e.g., MM/YYYY or Month YYYY).",
        "penalty_note": "Section 36(1) of Legal Metrology Act, 2009."
    },
    "RULE_6_1_E_MRP": {
        "rule_code": "RULE_6_1_E_MRP",
        "name": "Maximum Retail Price (MRP) & Tax Inclusivity",
        "category": "Pricing & Taxes",
        "reference": "Rule 6(1)(e) & Rule 2(m), Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "Clear declaration of MRP with recognized prefix (MRP, Maximum Retail Price) and the phrase 'inclusive of all taxes'.",
        "penalty_note": "Section 36(1) of Legal Metrology Act, 2009 for missing declaration; charging in excess of MRP attracts penalties up to ₹50,000 under Section 36(3)."
    },
    "RULE_6_1_R_UNIT_SALE_PRICE": {
        "rule_code": "RULE_6_1_R_UNIT_SALE_PRICE",
        "name": "Unit Sale Price (USP) Declaration",
        "category": "Pricing & Taxes",
        "reference": "Rule 6(1)(r), Legal Metrology (Packaged Commodities) Rules, 2011 (Amended)",
        "description": "Declaration of unit sale price per gram/ml for packages <1kg/1L, or per kg/L for packages >1kg/1L.",
        "penalty_note": "Section 36(1) of Legal Metrology Act, 2009 for non-declaration."
    },
    "RULE_6_2_CONSUMER_CARE": {
        "rule_code": "RULE_6_2_CONSUMER_CARE",
        "name": "Consumer Care Redressal Details",
        "category": "Mandatory Declarations",
        "reference": "Rule 6(2), Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "Name, address, telephone number, and email address of the person or office who can be contacted in case of consumer complaints.",
        "penalty_note": "Section 36(1) of Legal Metrology Act, 2009."
    },
    "RULE_6_1_N_COUNTRY_OF_ORIGIN": {
        "rule_code": "RULE_6_1_N_COUNTRY_OF_ORIGIN",
        "name": "Country of Origin (Imported Commodities)",
        "category": "Import & Origin",
        "reference": "Rule 6(1)(n), Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "Name of the country of origin or manufacture where the package is imported.",
        "penalty_note": "Section 36(1) of Legal Metrology Act, 2009."
    },
    "RULE_6_1_F_DIMENSIONS": {
        "rule_code": "RULE_6_1_F_DIMENSIONS",
        "name": "Size and Dimension Declarations",
        "category": "Physical Specifications",
        "reference": "Rule 6(1)(f), Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "Mandatory dimensions declaration for commodities where size is relevant (garments, bedsheets, tiles, paper, etc.).",
        "penalty_note": "Section 36(1) of Legal Metrology Act, 2009."
    },
    "RULE_6_3_4_STICKER_CHECK": {
        "rule_code": "RULE_6_3_4_STICKER_CHECK",
        "name": "Label Sticker & Modification Verification",
        "category": "Tampering & Visual Inspection",
        "reference": "Rule 6(3) & Rule 6(4), Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "Prohibits alteration of declarations by stickers except as explicitly permitted by notification or for imported items.",
        "penalty_note": "Marked UNABLE_TO_VERIFY / Requires Physical Verification: single 2D image cannot definitively determine adhesive substrate legitimacy."
    },
    "RULE_7_FONT_SIZE": {
        "rule_code": "RULE_7_FONT_SIZE",
        "name": "Minimum Font Height & Line Spacing",
        "category": "Typography & Legibility",
        "reference": "Rule 7 & Table I, Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "Minimum numeral and letter heights in physical millimeters based on net quantity brackets.",
        "penalty_note": "Marked UNABLE_TO_VERIFY: Standard OCR images lack calibrated physical millimeter scales without physical measurement targets."
    },
    "RULE_8_PDP": {
        "rule_code": "RULE_8_PDP",
        "name": "Principal Display Panel (PDP) Dimensions",
        "category": "Display Requirements",
        "reference": "Rule 8, Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "PDP area calculations (40% of height x width for rectangular, 40% of height x circumference for cylindrical).",
        "penalty_note": "Marked UNABLE_TO_VERIFY: 3D package geometry cannot be measured from a single cropped 2D label photograph."
    },
    "RULE_9_MANNER_OF_DECLARATION": {
        "rule_code": "RULE_9_MANNER_OF_DECLARATION",
        "name": "Language & Prominence of Declarations",
        "category": "Display Requirements",
        "reference": "Rule 9, Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "Declarations must be conspicuous, legible, and in Hindi (Devanagari script) or English.",
        "penalty_note": "Section 36(1) of Legal Metrology Act, 2009."
    },
    "RULE_THIRD_SCHEDULE": {
        "rule_code": "RULE_THIRD_SCHEDULE",
        "name": "Third Schedule 'When Packed' Restriction",
        "category": "Quantity & Measurement",
        "reference": "Third Schedule & Rule 11, Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "'When packed' declaration is restricted exclusively to soaps, lotions, and creams.",
        "penalty_note": "Unauthorized 'when packed' declarations on other commodities violate Rule 11."
    },
    "RULE_FOURTH_SCHEDULE": {
        "rule_code": "RULE_FOURTH_SCHEDULE",
        "name": "Fourth Schedule Specified Commodity Units",
        "category": "Quantity & Measurement",
        "reference": "Fourth Schedule, Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "Mandatory unit specification according to prescribed commodity classification.",
        "penalty_note": "Section 36(1) of Legal Metrology Act, 2009."
    },
    "RULE_SECOND_SCHEDULE": {
        "rule_code": "RULE_SECOND_SCHEDULE",
        "name": "Second Schedule Standard Packaging Sizes",
        "category": "Packaging Standards",
        "reference": "Second Schedule, Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "Prescribed standard packaging sizes for specified essential commodities.",
        "penalty_note": "Marked REQUIRES_VERIFICATION where recent amendments permit non-standard sizes provided USP is declared."
    },
    "RULE_24_WHOLESALE": {
        "rule_code": "RULE_24_WHOLESALE",
        "name": "Wholesale Package Provisions",
        "category": "Scope & Exemptions",
        "reference": "Rule 24, Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "Provisions applicable solely to wholesale packages (packages containing multiple retail packages).",
        "penalty_note": "NOT_APPLICABLE for retail packaging screening."
    },
    "OUT_OF_SCOPE_PHYSICAL": {
        "rule_code": "OUT_OF_SCOPE_PHYSICAL",
        "name": "Physical Testing & Maximum Permissible Error (MPE)",
        "category": "Out of Scope",
        "reference": "First Schedule & General Provisions, Legal Metrology Act, 2009",
        "description": "Physical weight verification, net mass error limits, and weighing instrument calibration.",
        "penalty_note": "OUT_OF_SCOPE / UNABLE_TO_VERIFY: Image analysis cannot perform physical gravimetric testing."
    },
    "RULE_ECOMMERCE_2026": {
        "rule_code": "RULE_ECOMMERCE_2026",
        "name": "E-Commerce Digital Platform Declarations",
        "category": "Platform Rules",
        "reference": "Rule 6(10), Legal Metrology (Packaged Commodities) Rules, 2011",
        "description": "Digital marketplace mandatory display of MRP, expiry, country of origin, and consumer care.",
        "penalty_note": "OUT_OF_SCOPE / UNABLE_TO_VERIFY: Physical label photographs cannot verify marketplace digital search filters."
    }
}
