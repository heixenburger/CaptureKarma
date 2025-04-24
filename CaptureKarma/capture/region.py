"""
Region selection functionality for the CaptureKarma Screen Capture Tool
"""
import pygetwindow as gw
from PyQt5 import QtWidgets, QtCore, QtGui


class RegionSelector:
    """Handles the selection of screen regions for capture"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def select_region(self):
        """
        Open a dialog to select a region to capture (monitor or window)
        Returns the region as a tuple (x, y, width, height) or None if canceled
        """
        self.parent.parent.status_bar.showMessage("Select a window or monitor to capture")
        
        # Create a dialog for selecting monitor or window
        dialog = QtWidgets.QDialog(self.parent)
        dialog.setWindowTitle("Select Capture Region")
        dialog.setMinimumWidth(500)
        dialog_layout = QtWidgets.QVBoxLayout(dialog)
        
        # Create tabs for different selection methods
        tab_widget = QtWidgets.QTabWidget()
        monitor_tab = QtWidgets.QWidget()
        window_tab = QtWidgets.QWidget()
        
        tab_widget.addTab(monitor_tab, "Select Monitor")
        tab_widget.addTab(window_tab, "Select Window")
        
        dialog_layout.addWidget(tab_widget)
        
        # Setup monitor selection tab
        self._setup_monitor_tab(monitor_tab)
        
        # Setup window selection tab
        self._setup_window_tab(window_tab)
        
        # Preview checkbox
        preview_cb = QtWidgets.QCheckBox("Attempt to show preview (may cause black screen on some systems)")
        preview_cb.setChecked(True)
        dialog_layout.addWidget(preview_cb)
        
        # Buttons
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | 
            QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog_layout.addWidget(buttons)
        
        # Show dialog and process result
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            try:
                current_tab = tab_widget.currentIndex()
                capture_region = None
                
                if current_tab == 0:  # Monitor tab
                    # Get selected monitor
                    monitor_idx = self.monitors_list.currentRow()
                    screen_geometry = QtWidgets.QApplication.desktop().screenGeometry(monitor_idx)
                    
                    # Set the capture region to the monitor dimensions
                    capture_region = (
                        screen_geometry.x(),
                        screen_geometry.y(),
                        screen_geometry.width(),
                        screen_geometry.height()
                    )
                    
                    # Generate a preview
                    region_name = f"Monitor {monitor_idx+1}"
                    self._generate_region_preview(region_name, capture_region, preview_cb.isChecked())
                    
                    self.parent.parent.status_bar.showMessage(
                        f"Selected monitor {monitor_idx+1} with region: {capture_region}"
                    )
                else:  # Window tab
                    # Get selected window
                    window_title = self.windows_list.currentItem().text()
                    
                    # Get window position and size
                    window = gw.getWindowsWithTitle(window_title)[0]
                    
                    # Set the capture region to the window dimensions
                    capture_region = (
                        window.left,
                        window.top,
                        window.width,
                        window.height
                    )
                    
                    # Generate a preview
                    self._generate_region_preview(window_title, capture_region, preview_cb.isChecked())
                    
                    self.parent.parent.status_bar.showMessage(
                        f"Selected window: {window_title} with region: {capture_region}"
                    )
                
                return capture_region
                
            except Exception as e:
                self.parent.parent.status_bar.showMessage(f"Error selecting region: {str(e)}")
                print(f"Error in region selection: {str(e)}")
                import traceback
                traceback.print_exc()
                return None
        else:
            self.parent.parent.status_bar.showMessage("Region selection canceled")
            return None
    
    def _setup_monitor_tab(self, tab):
        """Setup the monitor selection tab"""
        monitor_layout = QtWidgets.QVBoxLayout(tab)
        
        # Get all monitors
        self.monitors_list = QtWidgets.QListWidget()
        screen_count = QtWidgets.QApplication.desktop().screenCount()
        
        for i in range(screen_count):
            screen_geometry = QtWidgets.QApplication.desktop().screenGeometry(i)
            self.monitors_list.addItem(
                f"Monitor {i+1}: {screen_geometry.width()}x{screen_geometry.height()} "
                f"at ({screen_geometry.x()}, {screen_geometry.y()})"
            )
        
        if screen_count > 0:
            self.monitors_list.setCurrentRow(0)
            
        monitor_layout.addWidget(QtWidgets.QLabel("Select a monitor to capture:"))
        monitor_layout.addWidget(self.monitors_list)
    
    def _setup_window_tab(self, tab):
        """Setup the window selection tab"""
        window_layout = QtWidgets.QVBoxLayout(tab)
        
        # Get all window titles
        self.windows_list = QtWidgets.QListWidget()
        
        # Get all visible windows
        try:
            windows = gw.getAllTitles()
            
            for window_title in windows:
                if window_title and len(window_title.strip()) > 0:
                    self.windows_list.addItem(window_title)
                    
            if windows:
                self.windows_list.setCurrentRow(0)
        except ImportError:
            self.windows_list.addItem("pygetwindow library not installed. Run 'pip install pygetwindow'")
            self.windows_list.setEnabled(False)
        
        window_layout.addWidget(QtWidgets.QLabel("Select a window to capture:"))
        window_layout.addWidget(self.windows_list)
    
    def _generate_region_preview(self, title, region, try_real_preview=True):
        """Generate a preview of the selected region"""
        from CaptureKarma.utils.image_processing import ImageProcessor
        
        try:
            if try_real_preview:
                # Try to capture an actual screenshot for preview
                image_processor = ImageProcessor()
                pixmap = image_processor.capture_preview(region)
                
                if pixmap and not self._is_pixmap_black(pixmap):
                    # Scale and display the preview
                    self.parent.update_preview(pixmap)
                    return
            
            # If real preview fails or appears black, create a visual representation
            self._create_visual_preview(title, region)
                
        except Exception as e:
            print(f"Error generating preview: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Fallback to visual representation
            self._create_visual_preview(title, region)
    
    def _is_pixmap_black(self, pixmap):
        """Check if a pixmap is all black or empty"""
        if pixmap is None or pixmap.isNull():
            return True
            
        # Convert to image to check pixel values
        image = pixmap.toImage()
        if image.isNull():
            return True
            
        # Check a sample of pixels
        sample_size = min(100, pixmap.width() * pixmap.height())
        if sample_size == 0:
            return True
            
        black_count = 0
        step = max(1, pixmap.width() * pixmap.height() // sample_size)
        
        for i in range(0, pixmap.width() * pixmap.height(), step):
            x = i % pixmap.width()
            y = i // pixmap.width()
            if y < pixmap.height():
                pixel = image.pixel(x, y)
                # Check if pixel is black or almost black
                if QtGui.qRed(pixel) < 10 and QtGui.qGreen(pixel) < 10 and QtGui.qBlue(pixel) < 10:
                    black_count += 1
        
        # If more than 95% of sampled pixels are black, consider it a black image
        return black_count > (sample_size * 0.95)
    
    def _create_visual_preview(self, title, region):
        """Create a visual representation of the capture region"""
        x, y, width, height = region
        
        # Create a new image with a colored background
        image = QtGui.QImage(400, 300, QtGui.QImage.Format_RGB888)
        image.fill(QtGui.QColor(200, 220, 255))  # Light blue background
        
        # Create a painter to draw on the image
        painter = QtGui.QPainter(image)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw a border
        pen = QtGui.QPen(QtGui.QColor(100, 100, 200), 3)
        painter.setPen(pen)
        painter.drawRect(10, 10, 380, 280)
        
        # Add text information
        font = QtGui.QFont("Arial", 12)
        painter.setFont(font)
        painter.setPen(QtGui.QColor(0, 0, 100))
        
        # Draw the title and details
        painter.drawText(20, 40, f"Selected: {title}")
        painter.drawText(20, 70, f"Position: ({x}, {y})")
        painter.drawText(20, 100, f"Size: {width} × {height} pixels")
        painter.drawText(20, 150, "Note: Real preview not available.")
        painter.drawText(20, 180, "Capture will still work correctly.")
        
        # Draw a camera icon
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(QtGui.QColor(150, 150, 220))
        # Simple camera shape
        painter.drawRoundedRect(150, 200, 100, 60, 10, 10)
        painter.drawEllipse(185, 215, 30, 30)
        
        painter.end()
        
        # Convert to pixmap and display
        pixmap = QtGui.QPixmap.fromImage(image)
        self.parent.update_preview(pixmap)