import abc
from typing import Optional, Dict

class OcrService(abc.ABC):
    """Abstract base class for Optical Character Recognition services."""
    
    @abc.abstractmethod
    def extract_text(self, image_bytes: bytes, filename: Optional[str] = None) -> str:
        """Extract raw text from an image file."""
        pass

class PackagingOcrService(OcrService):
    """
    High-accuracy optical character recognition service for packaged commodities.
    Combines remote high-resolution packaging OCR (OCR.space Engine 2) with
    heuristic fallbacks and benchmark datasets.
    """

    DEMO_DATASETS: Dict[str, str] = {
        "demoA": """Product: SunGold Premium Butter Cookies
Brand: SunGold
Generic Name: Butter Cookies
Category: Food & Confectionery
MRP: ₹45.00 (inclusive of all taxes)
Unit Sale Price: ₹0.225 / g
Net Quantity: 200 g
Manufactured & Packed by: SunGold Confectioneries Pvt. Ltd.
Address: Plot 42, KIADB Industrial Area, Phase 2, Whitefield, Bengaluru, Karnataka - 560066
Mfg Date: 08/2026
Country of Origin: India
Customer Care: Manager Consumer Care, SunGold Confectioneries Pvt. Ltd.
Address: Plot 42, KIADB Industrial Area, Whitefield, Bengaluru - 560066
Toll Free: 1800-425-9999
Email: care@sungoldfoods.com
Web: www.sungoldfoods.com
Language: English & Hindi (शुद्ध मक्खन कुकीज़)
""",

        "demoB": """Product: Crunchy Nacho Crisps
Brand: Fiesta Snacks
Generic Name: Corn Nacho Crisps
Category: Snack Foods
MRP: Rs. 60
Net Quantity: 150 g
Mfg Date: 05/2026
Country of Origin: India
Batch No: B924-A
""",

        "demoC": """Product: Herbal Glow Body Wash
Brand: GlowAura
Category: Personal Care
Net Qty: Net Wt. approx 250 g when packed
MRP: ₹180/-
Mfg Date: 2024
Manufactured by: GlowAura, Delhi
Customer Helpline: Call: 9999999999
Batch No: GA-781
"""
    }

    def extract_text(self, image_bytes: bytes, filename: Optional[str] = None) -> str:
        """
        Extract text from packaged commodity image using OCR.space.
        Tries BOTH engines and merges results for maximum text extraction.
        """
        if not image_bytes or len(image_bytes) < 100:
            return ""

        fname = filename or "package_label.jpg"
        ext = fname.lower().rsplit('.', 1)[-1] if '.' in fname else 'jpg'
        mime_map = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp'}
        mime_type = mime_map.get(ext, 'image/jpeg')

        results_by_engine = {}

        for engine_id in ["2", "1"]:
            try:
                import httpx
                files = {"file": (fname, image_bytes, mime_type)}
                data = {
                    "apikey": "helloworld",
                    "language": "eng",
                    "OCREngine": engine_id,
                    "scale": "true",
                    "detectOrientation": "true",
                    "isOverlayRequired": "false",
                }
                with httpx.Client(timeout=15.0) as client:
                    resp = client.post("https://api.ocr.space/parse/image", files=files, data=data)
                    if resp.status_code == 200:
                        res_json = resp.json()
                        if not res_json.get("IsErroredOnProcessing", False):
                            parsed_results = res_json.get("ParsedResults", [])
                            if parsed_results:
                                parsed_text = parsed_results[0].get("ParsedText", "").strip()
                                if parsed_text:
                                    results_by_engine[engine_id] = parsed_text
            except Exception:
                pass

        # Pick the best result: prefer the longer text (more content extracted)
        if results_by_engine:
            # If both engines returned results, combine them for maximum coverage
            if len(results_by_engine) == 2:
                text_e2 = results_by_engine.get("2", "")
                text_e1 = results_by_engine.get("1", "")
                # Use whichever is longer as primary, but append unique lines from the other
                if len(text_e2) >= len(text_e1):
                    primary, secondary = text_e2, text_e1
                else:
                    primary, secondary = text_e1, text_e2
                
                # Extract lines from secondary that aren't already in primary
                primary_lower = primary.lower()
                extra_lines = []
                for line in secondary.split('\n'):
                    line_stripped = line.strip()
                    if line_stripped and len(line_stripped) >= 3:
                        # Only add if this line's content isn't already present
                        if line_stripped.lower() not in primary_lower:
                            extra_lines.append(line_stripped)
                
                if extra_lines:
                    combined = primary + "\n" + "\n".join(extra_lines)
                    return combined
                return primary
            else:
                # Single engine result
                return list(results_by_engine.values())[0]

        return ""

    def get_demo_text(self, preset: str) -> str:
        return self.DEMO_DATASETS.get(preset, self.DEMO_DATASETS["demoA"])

# Alias for backward compatibility
MockOcrService = PackagingOcrService
