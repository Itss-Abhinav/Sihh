import abc
from typing import Optional, Dict

class OcrService(abc.ABC):
    """Abstract base class for Optical Character Recognition services."""
    
    @abc.abstractmethod
    def extract_text(self, image_bytes: bytes, filename: Optional[str] = None) -> str:
        """Extract raw text from an image file."""
        pass

class MockOcrService(OcrService):
    """
    Mock OCR Service providing realistic packaged commodity text declarations
    matching standard Indian Legal Metrology pack formats.
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
        # If client-side OCR wasn't passed, attempt basic extraction or provide an honest unreadable notification
        import re
        try:
            text_candidate = image_bytes.decode('utf-8', errors='ignore')
            text_chunks = re.findall(r'[A-Za-z0-9\.,:\/₹\-\(\)\s]{5,}', text_candidate)
            candidate = " ".join(c.strip() for c in text_chunks if len(c.strip()) > 5)
            lines = [line.strip() for line in candidate.split('\n') if len(line.strip()) > 4]
            if len(lines) >= 3:
                return "\n".join(lines[:20])
        except Exception:
            pass
        return "Product: Scanned Packaged Commodity\nNote: Automated optical text recognition in progress. Please review extracted declarations."

    def get_demo_text(self, preset: str) -> str:
        return self.DEMO_DATASETS.get(preset, self.DEMO_DATASETS["demoA"])
