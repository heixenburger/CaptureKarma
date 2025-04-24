"""
Image processing utilities for the CaptureKarma Screen Capture Tool
"""
import numpy as np
import pyautogui
from PyQt5 import QtGui
from PIL import Image

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False


class ImageProcessor:
    """Handles image processing, conversion, and transformation functionality"""
    
    def capture_preview(self, region):
        """Capture a preview of the specified region"""
        if not region:
            return None
            
        try:
            print(f"Updating preview with region: {region}")
            
            # Try using MSS first (better for multi-monitor setups)
            if MSS_AVAILABLE:
                return self._capture_with_mss(region)
            
            # Fallback to PyAutoGUI
            return self._capture_with_pyautogui(region)
                
        except Exception as e:
            print(f"Error capturing preview: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _capture_with_mss(self, region):
        """Capture screenshot using MSS (better for multi-monitor)"""
        x, y, width, height = region
        
        try:
            with mss.mss() as sct:
                # Define the region to capture
                monitor = {"top": y, "left": x, "width": width, "height": height}
                
                # Capture the screenshot
                sct_img = sct.grab(monitor)
                
                # Convert to PIL Image
                screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                # Convert to QImage and then to QPixmap
                return self.pil_to_pixmap(screenshot)
        except Exception as e:
            print(f"MSS capture failed: {str(e)}")
            return None
    
    def _capture_with_pyautogui(self, region):
        """Capture screenshot using PyAutoGUI"""
        try:
            # Take the screenshot
            screenshot = pyautogui.screenshot(region=region)
            
            # Convert to QPixmap
            return self.pil_to_pixmap(screenshot)
        except Exception as e:
            print(f"PyAutoGUI capture failed: {str(e)}")
            return None
    
    def pil_to_pixmap(self, pil_image):
        """Convert PIL image to QPixmap"""
        if not pil_image:
            return None
            
        try:
            # Ensure the image is in RGB mode
            if pil_image.mode != "RGB":
                pil_image = pil_image.convert("RGB")
                
            # Get image dimensions
            width, height = pil_image.size
            
            # Convert PIL image to QImage
            buffer = pil_image.tobytes("raw", "RGB")
            qimage = QtGui.QImage(buffer, width, height, width * 3, QtGui.QImage.Format_RGB888)
            
            # Convert QImage to QPixmap
            return QtGui.QPixmap.fromImage(qimage)
        except Exception as e:
            print(f"Error in pil_to_pixmap: {str(e)}")
            # Return None on failure
            return None
    
    def is_image_black(self, pil_image):
        """Check if a PIL image is all or mostly black"""
        # Convert to numpy array for faster analysis
        img_array = np.array(pil_image)
        
        # Calculate the mean brightness across all channels
        mean_brightness = np.mean(img_array)
        
        # If mean brightness is very low, consider it black
        return mean_brightness < 10