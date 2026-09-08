# Legal Metrology (Packaged Commodities) Rules, 2011 — Rulebook 2026.2

## 1. Regulatory Authority & Scope
The Legal Metrology (Packaged Commodities) Rules, 2011 are framed under the **Legal Metrology Act, 2009 (Act 1 of 2010)** by the Department of Consumer Affairs, Ministry of Consumer Affairs, Food and Public Distribution, Government of India.

*Disclaimer: Automated screening result — not a legal determination. Development Rulebook 2026.2 reflects statutory consolidations and gazette notifications. Physical verification by licensed legal metrology officers is required for legal adjudication.*

---

## 2. Rulebook Catalog & Evaluation Specifications

| Rule Code | Statutory Provision | Field / Target | Conformance Requirement | Automated Status Handling |
|---|---|---|---|---|
| `RULE_3_SCOPE` | Rule 3 | Scope Exclusions | Packages >25kg or 25L (except cement/fertilizer up to 50kg), industrial packs, or institutional packs. | `NOT_APPLICABLE` for retail rules if scope exclusion matches. |
| `RULE_26_EXEMPTIONS` | Rule 26 | Small Measure Exemptions | Net weight/measure <=10g or 10ml, fast food packed by hotels/restaurants, farm produce >50kg, bidis, domestic LPG, and specific Drug Act formulations. | `NOT_APPLICABLE` for standard retail declarations if exemption matches. |
| `RULE_6_1_A_MANUFACTURER` | Rule 6(1)(a) & 10(1) | Manufacturer / Packer / Importer | Name and complete postal address (street, city, state, PIN). | `PASS` if structural address verified; `REQUIRES_VERIFICATION` if abbreviated (short address proviso); `FAIL` if missing. |
| `RULE_6_1_B_GENERIC_NAME` | Rule 6(1)(b) | Generic / Common Name | Common or generic name of commodity. | `PASS` if present; `FAIL` if missing. |
| `RULE_6_1_C_NET_QUANTITY` | Rule 6(1)(c) & Rules 11-13 | Net Quantity & Units | Standard SI units (g, kg, ml, l, cm, m, N, U). No prohibited qualifiers ("approx", "minimum", "nearly") or non-standard counts ("dozen", "gross"). | `FAIL` if prohibited qualifier or non-SI unit detected; `REQUIRES_VERIFICATION` if >=1000g declared in g; `PASS` otherwise. |
| `RULE_THIRD_SCHEDULE` | Third Schedule & Rule 11 | "When Packed" Restriction | "When packed" declaration permitted exclusively for soaps, lotions, and non-milk creams. | `FAIL` if "when packed" appears on non-permitted goods (e.g. body wash, food); `PASS` if permitted or absent. |
| `RULE_FOURTH_SCHEDULE` | Fourth Schedule | Commodity/Unit Mandates | Specific commodities must be declared in prescribed units (e.g., curd by weight, diesel by volume, garments by number). | `FAIL` if conflicting metric detected; `PASS` if compliant. |
| `RULE_6_1_D_MFG_DATE` | Rule 6(1)(d) | Date of Manufacture | Month and Year of manufacture, pre-packing, or import (MM/YYYY or Month YYYY). | `PASS` if valid month & year present; `FAIL` if missing or invalid. |
| `RULE_6_1_E_MRP` | Rule 6(1)(e) & Rule 2(m) | Maximum Retail Price | MRP with statutory prefix and mandatory phrase "inclusive of all taxes" (or "incl. of all taxes"). | `PASS` if prefix, monetary figure, and tax phrase present; `FAIL` if any component missing. |
| `RULE_6_1_R_UNIT_SALE_PRICE` | Rule 6(1)(r) (Amended) | Unit Sale Price (USP) | Unit price per gram/ml (for <=1kg/1L) or per kg/L (for >1kg/1L). | `PASS` if isolated; `REQUIRES_VERIFICATION` if absent on multi-unit packages. |
| `RULE_6_2_CONSUMER_CARE` | Rule 6(2) | Consumer Redressal | Name/office designation, address, telephone helpline, and email address for grievance redressal. | `PASS` if phone and email/address detected; `FAIL` if missing. |
| `RULE_6_1_N_COUNTRY_OF_ORIGIN` | Rule 6(1)(n) | Country of Origin | Mandatory for imported goods. | `PASS` for domestic or declared imports; `FAIL` if imported and undeclared. |
| `RULE_6_1_F_DIMENSIONS` | Rule 6(1)(f) | Dimensions / Size | Mandatory for garments, textiles, tiles, and dimensional goods. | `PASS` if declared when applicable; `NOT_APPLICABLE` for non-dimensional goods. |
| `RULE_6_3_4_STICKER_CHECK` | Rule 6(3) & 6(4) | Sticker Verification | Prohibition of altering declarations via adhesive stickers except where permitted by gazette notification. | `UNABLE_TO_VERIFY`: 2D image analysis cannot evaluate adhesive substrate legitimacy. |
| `RULE_7_FONT_SIZE` | Rule 7 & Table I | Minimum Font Height | Numeral and letter height in physical millimeters based on net weight brackets. | `UNABLE_TO_VERIFY`: Digital optical sensors cannot measure absolute physical millimeters without reference millimeter calibration targets. |
| `RULE_8_PDP` | Rule 8 | Principal Display Panel | Area must equal at least 40% of package face. | `UNABLE_TO_VERIFY`: Requires 3D geometric package measurements. |
| `RULE_9_MANNER_OF_DECLARATION` | Rule 9 | Language & Prominence | Declarations in Hindi (Devanagari script) or English. | `PASS` if Hindi or English detected; `FAIL` if unreadable/other. |
| `RULE_SECOND_SCHEDULE` | Second Schedule | Standard Pack Sizes | Prescribed standard packaging sizes for specified essential commodities. | `PASS` if matches schedule; `REQUIRES_VERIFICATION` if non-standard (valid if USP declared under recent amendments). |
| `RULE_24_WHOLESALE` | Rule 24 | Wholesale Packages | Rules governing wholesale multi-packs. | `NOT_APPLICABLE` for retail unit screening. |
| `OUT_OF_SCOPE_PHYSICAL` | LM Act 2009 | Physical Testing / MPE | Gravimetric weighing, tare weight, laboratory sampling, and Maximum Permissible Error tolerances. | `UNABLE_TO_VERIFY` / `OUT_OF_SCOPE`: Physical laboratory testing cannot be performed by image analysis. |
| `RULE_ECOMMERCE_2026` | Rule 6(10) | E-Commerce Platforms | Digital platform search display filters and web catalog rules. | `NOT_APPLICABLE`: Out of scope for physical package label analysis. |

---

## 3. Section 36 Penalty Context (Informational Only)
Under Section 36 of the Legal Metrology Act, 2009:
- **Section 36(1)**: Non-declaration or manufacturing/packing non-standard packages attracts a fine up to ₹25,000 for the first offence, ₹50,000 for the second offence, and up to ₹1,00,000 or imprisonment up to one year for subsequent offences.
- **Section 36(2)**: Selling or packaging non-standard weights or units.
- **Section 36(3)**: Charging in excess of the Maximum Retail Price (MRP) attracts fines up to ₹50,000.

*Note: Penalty information in LABELCHECK is provided for informational and educational context only and never determines whether a check passes or fails.*