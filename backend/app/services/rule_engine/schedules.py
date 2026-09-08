from typing import Dict, Set, List

# Third Schedule: Commodities permissible for 'when packed' quantity declaration
THIRD_SCHEDULE_COMMODITIES: Set[str] = {
    "soap", "soaps", "toilet soap", "laundry soap",
    "lotion", "lotions", "body lotion", "skin lotion",
    "cream", "creams", "face cream", "moisturizing cream", "cold cream"
}

# Fourth Schedule: Commodities and mandated units of declaration
FOURTH_SCHEDULE_MAPPINGS: Dict[str, str] = {
    "aerosol_products": "weight",
    "curd": "weight",
    "electric_cables": "length_or_weight",
    "fruits": "number_or_weight",
    "industrial_diesel": "volume",
    "ice_cream": "weight",
    "frozen_products": "weight",
    "lpg": "weight",
    "readymade_garments": "number",
    "sauces": "weight",
    "tyres": "number",
    "tubes": "number",
    "yarn": "weight_or_length",
    "cosmetics": "weight_or_measure"
}

# Prohibited qualifying terms under Rule 13
PROHIBITED_QUALIFYING_TERMS: List[str] = [
    "approx",
    "approximately",
    "around",
    "about",
    "nearly",
    "minimum",
    "not less than",
    "average"
]

# Prohibited count units under Rule 13(5)
PROHIBITED_COUNT_UNITS: List[str] = [
    "dozen",
    "score",
    "gross"
]

# Standard SI Units recognized under Legal Metrology Rules
VALID_SI_UNITS: Set[str] = {
    "g", "kg", "ml", "l", "cm", "m", "sq_dm", "sq_m", "cu_cm", "cu_m", "n", "u", "units", "unit"
}

# Second Schedule: Standard Package Sizes reference
SECOND_SCHEDULE_DATA: Dict[str, List[str]] = {
    "biscuits": ["25g", "50g", "75g", "100g", "150g", "200g", "250g", "300g", "500g", "1kg"],
    "bread": ["100g", "200g", "400g", "800g"],
    "tea": ["25g", "50g", "100g", "250g", "500g", "1kg"],
    "coffee": ["25g", "50g", "100g", "200g", "500g", "1kg"],
    "salt": ["500g", "1kg", "2kg", "5kg"],
    "milk_powder": ["100g", "200g", "500g", "1kg"],
    "detergents": ["100g", "200g", "500g", "1kg", "2kg", "3kg", "5kg"],
    "soaps": ["25g", "50g", "75g", "100g", "125g", "150g"],
    "mineral_water": ["100ml", "200ml", "250ml", "300ml", "500ml", "750ml", "1l", "2l", "5l"],
    "cement": ["1kg", "2kg", "5kg", "10kg", "20kg", "25kg", "50kg"],
    "paints": ["50ml", "100ml", "200ml", "500ml", "1l", "2l", "4l", "10l", "20l"]
}
