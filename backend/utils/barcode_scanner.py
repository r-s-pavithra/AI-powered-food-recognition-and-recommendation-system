import cv2
import numpy as np
from pyzbar import pyzbar
from PIL import Image
import io

def decode_barcode(image_bytes):
    """
    Decode barcode from image bytes
    Returns: barcode number or None
    """
    try:
        # Convert bytes to image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Decode barcodes
        barcodes = pyzbar.decode(img_array)
        
        if barcodes:
            # Return the first barcode found
            barcode_data = barcodes[0].data.decode('utf-8')
            barcode_type = barcodes[0].type
            
            return {
                "barcode": barcode_data,
                "type": barcode_type,
                "success": True
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

def enhance_image_for_barcode(image_bytes):
    """
    Enhance image to improve barcode detection
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Try decoding on enhanced image
        barcodes = pyzbar.decode(thresh)
        
        if barcodes:
            return {
                "barcode": barcodes[0].data.decode('utf-8'),
                "type": barcodes[0].type,
                "success": True
            }
        
        return {"success": False, "error": "No barcode found after enhancement"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}
