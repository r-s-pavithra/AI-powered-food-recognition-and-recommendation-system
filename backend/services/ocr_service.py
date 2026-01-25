from typing import Optional, Dict

class OCRService:
    """Service for OCR date extraction (Week 4)"""
    
    @staticmethod
    def extract_dates(image_path: str) -> Optional[Dict]:
        """
        Extract dates from product image
        Will be implemented in Week 4 with Tesseract OCR
        """
        return {
            "message": "OCR date extraction coming in Week 4",
            "mfg_date": None,
            "exp_date": None,
            "confidence": 0.0
        }
