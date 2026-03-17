"""
Barcode scanning utilities using OpenCV and pyzbar
Handles various image formats: RGB, RGBA, Grayscale
"""
import cv2
import numpy as np
from pyzbar import pyzbar
from PIL import Image
import io
from typing import Dict, Any


def decode_barcode(image_bytes: bytes) -> Dict[str, Any]:
    """
    Decode barcode from image bytes
    
    Args:
        image_bytes: Raw image bytes from uploaded file
        
    Returns:
        Dictionary with success status and barcode data or error
        {
            "success": bool,
            "barcode": str (if found),
            "type": str (if found),
            "error": str (if failed)
        }
    """
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert PIL Image to numpy array
        img_array = np.array(image)
        
        # Handle different image formats
        if len(img_array.shape) == 2:
            # Grayscale image (1 channel) - convert to RGB
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        elif len(img_array.shape) == 3:
            if img_array.shape[2] == 4:
                # RGBA image (4 channels) - convert to RGB
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            elif img_array.shape[2] == 3:
                # RGB image - already good, no conversion needed
                pass
        
        # Decode barcodes using pyzbar
        barcodes = pyzbar.decode(img_array)
        
        if barcodes:
            # Return the first barcode found
            barcode_data = barcodes[0].data.decode('utf-8').strip()
            barcode_type = barcodes[0].type
            
            return {
                "success": True,
                "barcode": barcode_data,
                "type": barcode_type
            }
        else:
            return {
                "success": False,
                "error": "No barcode detected in image"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing image: {str(e)}"
        }


def enhance_image_for_barcode(image_bytes: bytes) -> Dict[str, Any]:
    """
    Enhance image quality to improve barcode detection
    Applies various image processing techniques
    
    Args:
        image_bytes: Raw image bytes from uploaded file
        
    Returns:
        Dictionary with success status and barcode data or error
    """
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale for processing
        if len(img_array.shape) == 2:
            # Already grayscale
            gray = img_array
        elif len(img_array.shape) == 3:
            if img_array.shape[2] == 4:
                # RGBA - convert to grayscale
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)
            else:
                # RGB - convert to grayscale
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Try multiple enhancement techniques
        enhanced_images = []
        
        # 1. Original grayscale
        enhanced_images.append(("original_gray", gray))
        
        # 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced_clahe = clahe.apply(gray)
        enhanced_images.append(("clahe", enhanced_clahe))
        
        # 3. Otsu's thresholding
        _, thresh_otsu = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        enhanced_images.append(("otsu_threshold", thresh_otsu))
        
        # 4. Adaptive thresholding
        thresh_adaptive = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        enhanced_images.append(("adaptive_threshold", thresh_adaptive))
        
        # 5. Denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        enhanced_images.append(("denoised", denoised))
        
        # 6. Denoising + Threshold
        _, thresh_denoised = cv2.threshold(
            denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        enhanced_images.append(("denoised_threshold", thresh_denoised))
        
        # Try decoding on each enhanced version
        for method_name, processed_img in enhanced_images:
            barcodes = pyzbar.decode(processed_img)
            
            if barcodes:
                barcode_data = barcodes[0].data.decode('utf-8').strip()
                barcode_type = barcodes[0].type
                
                return {
                    "success": True,
                    "barcode": barcode_data,
                    "type": barcode_type,
                    "method": method_name
                }
        
        # No barcode found even after all enhancements
        return {
            "success": False,
            "error": "No barcode detected even after image enhancement"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error enhancing image: {str(e)}"
        }


# Optional: Function to validate barcode format
def validate_barcode(barcode: str, barcode_type: str) -> bool:
    """
    Validate barcode format based on type
    
    Args:
        barcode: Barcode string
        barcode_type: Type of barcode (EAN13, UPCA, etc.)
        
    Returns:
        True if valid, False otherwise
    """
    if barcode_type == "EAN13":
        return len(barcode) == 13 and barcode.isdigit()
    elif barcode_type == "UPCA":
        return len(barcode) == 12 and barcode.isdigit()
    elif barcode_type == "EAN8":
        return len(barcode) == 8 and barcode.isdigit()
    elif barcode_type in ["CODE128", "CODE39"]:
        return len(barcode) > 0
    elif barcode_type == "QRCODE":
        return len(barcode) > 0
    else:
        return True  # Unknown types pass validation