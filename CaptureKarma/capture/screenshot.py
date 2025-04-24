"""
Screenshot capture functionality for the CaptureKarma Screen Capture Tool
"""
import os
import datetime
import threading
import pyautogui
from PIL import Image

from CaptureKarma.utils.image_processing import ImageProcessor
from CaptureKarma.utils.scrolling import ScrollingManager


class ScreenshotCapture:
    """Handles screenshot capturing functionality"""
    
    def __init__(self, parent):
        self.parent = parent
        self.image_processor = ImageProcessor()
        self.scrolling_manager = ScrollingManager()
    
    def take_screenshot(self, region, output_dir, 
                       scrolling_enabled=False, scroll_amount=0, 
                       scroll_duration=0, scroll_step=5):
        """
        Take a screenshot of the specified region
        
        Args:
            region: Tuple (x, y, width, height) defining the region to capture
            output_dir: Directory to save the screenshot
            scrolling_enabled: Whether to perform scrolling before capture
            scroll_amount: Amount to scroll (negative for down, positive for up)
            scroll_duration: Duration of scrolling in seconds
            scroll_step: Size of each scroll step (smaller = smoother)
        """
        if not region:
            self.parent.parent.status_bar.showMessage("Please select a region first")
            return
        
        try:
            # Create a timestamp for the filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(output_dir, f"screenshot_{timestamp}.png")
            
            # Log what we're doing
            self.parent.parent.status_bar.showMessage("Preparing to take screenshot...")
            
            # If scrolling is enabled, perform scrolling and capture
            if scrolling_enabled:
                self._take_screenshot_with_scrolling(
                    region, filename, scroll_amount, scroll_duration, scroll_step
                )
            else:
                # Take the screenshot without scrolling
                self._take_screenshot_direct(region, filename)
            
            # Try to show a small preview thumbnail
            self._show_thumbnail_preview(filename)
            
            # Open the folder so the user can check the screenshot
            self.parent.parent.open_output_folder()
            
        except Exception as e:
            self.parent.parent.status_bar.showMessage(f"Error taking screenshot: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _take_screenshot_direct(self, region, filename):
        """Take a direct screenshot without scrolling"""
        try:
            # Try using MSS first (better for multi-monitor setups)
            try:
                import mss
                
                with mss.mss() as sct:
                    # Get region dimensions
                    x, y, width, height = region
                    
                    # Define the region to capture
                    monitor = {"top": y, "left": x, "width": width, "height": height}
                    
                    # Capture the screenshot
                    sct_img = sct.grab(monitor)
                    
                    # Convert to PIL Image
                    from PIL import Image
                    screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    
                    self.parent.parent.status_bar.showMessage("Screenshot taken using MSS (Windows native API)")
            except Exception as e:
                print(f"MSS screenshot failed: {str(e)}, trying fallback")
                
                # Second attempt: Try standard pyautogui approach
                screenshot = pyautogui.screenshot(region=region)
                self.parent.parent.status_bar.showMessage("Screenshot taken using PyAutoGUI")
            
            # Save the screenshot and check if it's black
            screenshot.save(filename)
            
            # Check if the screenshot is all black
            if self.image_processor.is_image_black(screenshot):
                self.parent.parent.status_bar.showMessage(
                    "Warning: Screenshot appears to be all black. "
                    "This may be due to Windows security restrictions."
                )
            else:
                self.parent.parent.status_bar.showMessage(f"Screenshot saved to {filename}")
                
            return screenshot
            
        except Exception as e:
            self.parent.parent.status_bar.showMessage(f"Error taking direct screenshot: {str(e)}")
            raise
    
    def _take_screenshot_with_scrolling(self, region, filename, scroll_amount, scroll_duration, scroll_step):
        """Take a screenshot after performing scrolling"""
        self.parent.parent.status_bar.showMessage("Taking screenshot with scrolling...")
        
        # Wait a moment to switch to target window
        self.parent.parent.status_bar.showMessage("Switch to your target window! Taking screenshot in 3 seconds...")
        
        try:
            # Move mouse to capture region center to ensure scrolling works
            x = region[0] + region[2] // 2
            y = region[1] + region[3] // 2
            self.scrolling_manager.smooth_move(x, y, duration=0.5)
            pyautogui.click()
            
            # Perform the scroll
            self.scrolling_manager.smooth_scroll(
                scroll_amount,
                scroll_duration,
                scroll_step,
                status_callback=lambda msg: self.parent.parent.status_bar.showMessage(msg)
            )
            
            # Take final screenshot
            self._take_screenshot_direct(region, filename)
            
        except Exception as e:
            self.parent.parent.status_bar.showMessage(f"Error during scrolling screenshot: {str(e)}")
            raise
    
    def _show_thumbnail_preview(self, filename):
        """Show a small thumbnail preview of the captured screenshot"""
        try:
            from PyQt5 import QtWidgets, QtCore, QtGui
            
            # Load the image
            image = Image.open(filename)
            
            # Create a small thumbnail preview
            thumb = image.copy()
            thumb.thumbnail((200, 200))
            
            # Convert to QPixmap
            pixmap = self.image_processor.pil_to_pixmap(thumb)
            if not pixmap:
                return
            
            # Show a smaller thumbnail in the corner
            small_preview = QtWidgets.QLabel(self.parent)
            small_preview.setPixmap(pixmap)
            small_preview.setStyleSheet("background-color: white; border: 1px solid black;")
            small_preview.setFixedSize(200, 200)
            small_preview.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
            small_preview.show()
            
            # Auto close after 3 seconds
            QtCore.QTimer.singleShot(3000, small_preview.close)
        except Exception as e:
            print(f"Error showing thumbnail: {str(e)}")