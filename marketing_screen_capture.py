import pyautogui
import time
import sys
import os
import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
import cv2
import numpy as np
import threading

# Safety feature - move mouse to top-left corner to abort script
pyautogui.FAILSAFE = True

class MarketingScreenCaptureTool(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Marketing Screen Capture Tool")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize variables
        self.capture_region = None
        self.is_recording = False
        self.recording_thread = None
        self.is_stopping_recording = False  # Lock to prevent multiple stop operations
        self.output_dir = os.path.join(os.path.expanduser("~"), "Documents", "MarketingCaptures")
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Main layout
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        
        # Create tabs
        self.tabs = QtWidgets.QTabWidget()
        self.capture_tab = QtWidgets.QWidget()
        self.settings_tab = QtWidgets.QWidget()
        
        self.tabs.addTab(self.capture_tab, "Capture")
        self.tabs.addTab(self.settings_tab, "Settings")
        
        main_layout.addWidget(self.tabs)
        
        # Setup tabs
        self.setup_capture_tab()
        self.setup_settings_tab()
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
        # Load settings
        self.load_settings()
        
    def setup_capture_tab(self):
        layout = QtWidgets.QVBoxLayout(self.capture_tab)
        
        # Preview area
        self.preview_label = QtWidgets.QLabel("Preview will appear here")
        self.preview_label.setAlignment(QtCore.Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.preview_label.setMinimumHeight(300)
        layout.addWidget(self.preview_label)
        
        # Buttons area
        buttons_layout = QtWidgets.QHBoxLayout()
        
        self.select_region_btn = QtWidgets.QPushButton("Select Region")
        self.select_region_btn.clicked.connect(self.select_capture_region)
        buttons_layout.addWidget(self.select_region_btn)
        
        self.take_screenshot_btn = QtWidgets.QPushButton("Take Screenshot")
        self.take_screenshot_btn.clicked.connect(self.take_screenshot)
        self.take_screenshot_btn.setEnabled(False)
        buttons_layout.addWidget(self.take_screenshot_btn)
        
        self.record_btn = QtWidgets.QPushButton("Start Recording")
        self.record_btn.clicked.connect(self.toggle_recording)
        self.record_btn.setEnabled(False)
        buttons_layout.addWidget(self.record_btn)
        
        layout.addLayout(buttons_layout)
        
        # Scrolling options
        scroll_group = QtWidgets.QGroupBox("Scrolling Options")
        scroll_layout = QtWidgets.QVBoxLayout(scroll_group)
        
        self.enable_scrolling_cb = QtWidgets.QCheckBox("Enable Scrolling During Capture")
        scroll_layout.addWidget(self.enable_scrolling_cb)
        
        scroll_params_layout = QtWidgets.QFormLayout()
        
        self.scroll_amount_spin = QtWidgets.QSpinBox()
        self.scroll_amount_spin.setRange(-10000, 10000)
        self.scroll_amount_spin.setValue(-1000)
        self.scroll_amount_spin.setSingleStep(100)
        scroll_params_layout.addRow("Scroll Amount (- for down, + for up):", self.scroll_amount_spin)
        
        self.scroll_duration_spin = QtWidgets.QDoubleSpinBox()
        self.scroll_duration_spin.setRange(1.0, 60.0)
        self.scroll_duration_spin.setValue(10.0)
        self.scroll_duration_spin.setSingleStep(0.5)
        scroll_params_layout.addRow("Scroll Duration (seconds):", self.scroll_duration_spin)
        
        self.scroll_step_spin = QtWidgets.QSpinBox()
        self.scroll_step_spin.setRange(1, 100)
        self.scroll_step_spin.setValue(5)
        scroll_params_layout.addRow("Scroll Step Size (smaller = smoother):", self.scroll_step_spin)
        
        scroll_layout.addLayout(scroll_params_layout)
        layout.addWidget(scroll_group)
        
        # Output info
        output_group = QtWidgets.QGroupBox("Output Information")
        output_layout = QtWidgets.QVBoxLayout(output_group)
        
        self.output_path_label = QtWidgets.QLabel(f"Output Path: {self.output_dir}")
        output_layout.addWidget(self.output_path_label)
        
        self.open_folder_btn = QtWidgets.QPushButton("Open Output Folder")
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        output_layout.addWidget(self.open_folder_btn)
        
        layout.addWidget(output_group)
    
    def setup_settings_tab(self):
        layout = QtWidgets.QVBoxLayout(self.settings_tab)
        
        # Video settings
        video_group = QtWidgets.QGroupBox("Video Settings")
        video_layout = QtWidgets.QFormLayout(video_group)
        
        self.fps_spin = QtWidgets.QSpinBox()
        self.fps_spin.setRange(10, 60)
        self.fps_spin.setValue(30)  # Default 30 FPS for smoother video
        video_layout.addRow("Recording FPS:", self.fps_spin)
        
        self.video_quality_combo = QtWidgets.QComboBox()
        self.video_quality_combo.addItems(["Low", "Medium", "High"])
        self.video_quality_combo.setCurrentIndex(2)  # High quality default
        video_layout.addRow("Video Quality:", self.video_quality_combo)
        
        # Output format selection
        self.output_format_combo = QtWidgets.QComboBox()
        self.output_format_combo.addItems(["MP4", "AVI"])
        self.output_format_combo.setCurrentIndex(0)  # MP4 default
        video_layout.addRow("Output Format:", self.output_format_combo)
        
        layout.addWidget(video_group)
        
        # Output settings
        output_group = QtWidgets.QGroupBox("Output Settings")
        output_layout = QtWidgets.QVBoxLayout(output_group)
        
        path_layout = QtWidgets.QHBoxLayout()
        self.output_path_edit = QtWidgets.QLineEdit(self.output_dir)
        self.output_path_edit.setReadOnly(True)
        path_layout.addWidget(self.output_path_edit)
        
        browse_btn = QtWidgets.QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_output_folder)
        path_layout.addWidget(browse_btn)
        
        output_layout.addLayout(path_layout)
        
        layout.addWidget(output_group)
        
        # Add save settings button
        save_btn = QtWidgets.QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        # Add spacer at the bottom
        layout.addStretch()
    
    def select_capture_region(self):
        self.status_bar.showMessage("Select a window or monitor to capture")
        
        # Create a dialog for selecting monitor or window
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Select Capture Region")
        dialog.setMinimumWidth(500)
        dialog_layout = QtWidgets.QVBoxLayout(dialog)
        
        # Create tabs for different selection methods
        tab_widget = QtWidgets.QTabWidget()
        window_tab = QtWidgets.QWidget()
        monitor_tab = QtWidgets.QWidget()
        
        tab_widget.addTab(monitor_tab, "Select Monitor")
        tab_widget.addTab(window_tab, "Select Window")
        
        dialog_layout.addWidget(tab_widget)
        
        # Setup monitor selection tab
        monitor_layout = QtWidgets.QVBoxLayout(monitor_tab)
        
        # Get all monitors
        monitors_list = QtWidgets.QListWidget()
        screen_count = QtWidgets.QApplication.desktop().screenCount()
        
        for i in range(screen_count):
            screen_geometry = QtWidgets.QApplication.desktop().screenGeometry(i)
            monitors_list.addItem(f"Monitor {i+1}: {screen_geometry.width()}x{screen_geometry.height()} at ({screen_geometry.x()}, {screen_geometry.y()})")
        
        if screen_count > 0:
            monitors_list.setCurrentRow(0)
            
        monitor_layout.addWidget(QtWidgets.QLabel("Select a monitor to capture:"))
        monitor_layout.addWidget(monitors_list)
        
        # Setup window selection tab
        window_layout = QtWidgets.QVBoxLayout(window_tab)
        
        # Get all window titles
        windows_list = QtWidgets.QListWidget()
        
        # Get all visible windows using pyautogui
        try:
            import pygetwindow as gw
            windows = gw.getAllTitles()
            
            for window_title in windows:
                if window_title and len(window_title.strip()) > 0:
                    windows_list.addItem(window_title)
                    
            if windows:
                windows_list.setCurrentRow(0)
        except ImportError:
            windows_list.addItem("pygetwindow library not installed. Run 'pip install pygetwindow'")
            windows_list.setEnabled(False)
        
        window_layout.addWidget(QtWidgets.QLabel("Select a window to capture:"))
        window_layout.addWidget(windows_list)
        
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
                
                if current_tab == 0:  # Monitor tab
                    # Get selected monitor
                    monitor_idx = monitors_list.currentRow()
                    screen_geometry = QtWidgets.QApplication.desktop().screenGeometry(monitor_idx)
                    
                    # Set the capture region to the monitor dimensions
                    self.capture_region = (
                        screen_geometry.x(),
                        screen_geometry.y(),
                        screen_geometry.width(),
                        screen_geometry.height()
                    )
                    
                    # Generate a graphical representation for preview
                    self.generate_region_preview(f"Monitor {monitor_idx+1}", self.capture_region, preview_cb.isChecked())
                    
                    self.status_bar.showMessage(f"Selected monitor {monitor_idx+1} with region: {self.capture_region}")
                else:  # Window tab
                    # Get selected window
                    window_title = windows_list.currentItem().text()
                    
                    # Get window position and size
                    import pygetwindow as gw
                    window = gw.getWindowsWithTitle(window_title)[0]
                    
                    # Set the capture region to the window dimensions
                    self.capture_region = (
                        window.left,
                        window.top,
                        window.width,
                        window.height
                    )
                    
                    # Generate a graphical representation for preview
                    self.generate_region_preview(window_title, self.capture_region, preview_cb.isChecked())
                    
                    self.status_bar.showMessage(f"Selected window: {window_title} with region: {self.capture_region}")
                
                # Enable the buttons
                self.take_screenshot_btn.setEnabled(True)
                self.record_btn.setEnabled(True)
                
            except Exception as e:
                self.status_bar.showMessage(f"Error selecting region: {str(e)}")
                print(f"Error in region selection: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            self.status_bar.showMessage("Region selection canceled")

    def generate_region_preview(self, title, region, try_real_preview=True):
        """Generate a preview of the selected region using multiple methods"""
        try:
            if try_real_preview:
                # First attempt: try to capture the actual screenshot
                print(f"Attempting to capture actual screenshot of {title} at {region}")
                
                # Try different screen capture methods for different monitors
                try:
                    x, y, width, height = region
                    
                    # Try MSS library first (better for multi-monitor setups)
                    try:
                        import mss
                        with mss.mss() as sct:
                            # MSS uses a different monitor indexing system
                            # Convert region coordinates to monitor-specific coordinates
                            monitor = {"top": y, "left": x, "width": width, "height": height}
                            sct_img = sct.grab(monitor)
                            
                            # Convert to PIL Image
                            from PIL import Image
                            screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                            
                            # Convert to QImage
                            qimage = self.pil_to_qimage(screenshot)
                            pixmap = QtGui.QPixmap.fromImage(qimage)
                            
                            # Scale pixmap to fit the preview label while maintaining aspect ratio
                            scaled_pixmap = pixmap.scaled(
                                self.preview_label.width(), 
                                self.preview_label.height(),
                                QtCore.Qt.KeepAspectRatio
                            )
                            
                            # Set the pixmap to the label
                            self.preview_label.setPixmap(scaled_pixmap)
                            print("Preview updated successfully using MSS")
                            return  # Exit function if successful
                    except Exception as mss_error:
                        print(f"MSS preview failed: {str(mss_error)}, trying fallback methods")
                    
                    # Fallback to standard PyAutoGUI method
                    self.update_preview()
                except Exception as e:
                    print(f"All preview methods failed: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
                    # Force fallback to visual representation
                    raise Exception("Preview capture failed")
                
            # If the real preview appears black or fails, create a visual representation
            # Check if preview is empty or all black
            pixmap = self.preview_label.pixmap()
            if not pixmap or self.is_pixmap_black(pixmap):
                print("Preview appears black or failed, creating visual representation")
                self.create_visual_preview(title, region)
                
        except Exception as e:
            print(f"Error generating preview: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Fallback to visual representation
            self.create_visual_preview(title, region)
    
    def is_pixmap_black(self, pixmap):
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
    
    def create_visual_preview(self, title, region):
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
        self.preview_label.setPixmap(pixmap)
    
    def update_preview(self):
        if self.capture_region:
            try:
                print(f"Updating preview with region: {self.capture_region}")
                # Take the screenshot
                screenshot = pyautogui.screenshot(region=self.capture_region)
                print(f"Screenshot captured, size: {screenshot.width}x{screenshot.height}")
                
                # Convert to QImage
                qimage = self.pil_to_qimage(screenshot)
                
                # Create pixmap and scale it
                pixmap = QtGui.QPixmap.fromImage(qimage)
                print(f"Pixmap created, size: {pixmap.width()}x{pixmap.height()}")
                
                # Scale pixmap to fit the preview label while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.preview_label.width(), 
                    self.preview_label.height(),
                    QtCore.Qt.KeepAspectRatio
                )
                
                # Set the pixmap to the label
                self.preview_label.setPixmap(scaled_pixmap)
                print("Preview updated successfully")
            except Exception as e:
                print(f"Error updating preview: {str(e)}")
                import traceback
                traceback.print_exc()
                self.status_bar.showMessage(f"Error updating preview: {str(e)}")
                
                # Try a fallback approach
                try:
                    # Use a different approach for the preview
                    self.status_bar.showMessage("Using fallback preview method...")
                    fallback_message = f"Selected region: {self.capture_region}"
                    self.preview_label.setText(fallback_message)
                except:
                    pass
    
    def pil_to_qimage(self, pil_image):
        """Convert PIL image to QImage with better error handling"""
        try:
            # Ensure the image is in RGB mode
            if pil_image.mode != "RGB":
                pil_image = pil_image.convert("RGB")
                
            # Get image dimensions
            width, height = pil_image.size
            print(f"Converting PIL image size {width}x{height} to QImage")
            
            # Convert PIL image to QImage
            buffer = pil_image.tobytes("raw", "RGB")
            qimage = QtGui.QImage(buffer, width, height, width * 3, QtGui.QImage.Format_RGB888)
            
            if qimage.isNull():
                print("QImage is null after conversion")
                # Try alternative conversion method
                bytearr = QtCore.QByteArray(buffer)
                buffer = QtCore.QBuffer(bytearr)
                buffer.open(QtCore.QIODevice.ReadOnly)
                qimage = QtGui.QImage()
                qimage.load(buffer, "PPM")
                
            return qimage
        except Exception as e:
            print(f"Error in pil_to_qimage: {str(e)}")
            # Return a simple colored QImage as fallback
            fallback = QtGui.QImage(400, 300, QtGui.QImage.Format_RGB888)
            fallback.fill(QtGui.QColor(200, 200, 255))  # Light blue as fallback
            return fallback
    
    def take_screenshot(self):
        if not self.capture_region:
            self.status_bar.showMessage("Please select a region first")
            return
        
        try:
            # Create a timestamp for the filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, f"screenshot_{timestamp}.png")
            
            # Get region dimensions
            x, y, width, height = self.capture_region
            
            # Try using a different screenshot approach that works better with Windows security
            self.status_bar.showMessage("Preparing to take screenshot...")
            
            try:
                # First attempt: Try native Windows API for screen capture with MSS library
                import mss
                
                with mss.mss() as sct:
                    # Define the region to capture
                    monitor = {"top": y, "left": x, "width": width, "height": height}
                    
                    # Capture the screenshot
                    sct_img = sct.grab(monitor)
                    
                    # Convert to PIL Image
                    from PIL import Image
                    screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    
                    self.status_bar.showMessage("Screenshot taken using MSS (Windows native API)")
            except Exception as e:
                print(f"MSS screenshot failed: {str(e)}, trying fallback")
                
                # Second attempt: Try standard pyautogui approach
                screenshot = pyautogui.screenshot(region=self.capture_region)
                self.status_bar.showMessage("Screenshot taken using PyAutoGUI")
            
            # If scrolling is enabled, perform scrolling and capture
            if self.enable_scrolling_cb.isChecked():
                self.status_bar.showMessage("Taking screenshot with scrolling...")
                
                # Wait a moment to switch to target window
                self.status_bar.showMessage("Switch to your target window! Taking screenshot in 3 seconds...")
                time.sleep(3)
                
                # Move mouse to capture region center to ensure scrolling works
                x = self.capture_region[0] + self.capture_region[2] // 2
                y = self.capture_region[1] + self.capture_region[3] // 2
                self.smooth_move(x, y, duration=0.5)
                pyautogui.click()
                
                # Perform the scroll
                self.smooth_scroll(
                    self.scroll_amount_spin.value(),
                    self.scroll_duration_spin.value(),
                    self.scroll_step_spin.value()
                )
                
                # Take final screenshot with the best method available
                try:
                    with mss.mss() as sct:
                        monitor = {"top": y, "left": x, "width": width, "height": height}
                        sct_img = sct.grab(monitor)
                        screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                except:
                    screenshot = pyautogui.screenshot(region=self.capture_region)
            
            # Save the screenshot and check if it's black
            screenshot.save(filename)
            
            # Check if the screenshot is all black
            if self.is_image_black(screenshot):
                self.status_bar.showMessage("Warning: Screenshot appears to be all black. This may be due to Windows security restrictions.")
            else:
                self.status_bar.showMessage(f"Screenshot saved to {filename}")
            
            # Try to show a small preview thumbnail
            try:
                # Create a small thumbnail preview
                thumb = screenshot.copy()
                thumb.thumbnail((200, 200))
                
                qimage = self.pil_to_qimage(thumb)
                pixmap = QtGui.QPixmap.fromImage(qimage)
                
                # Show a smaller thumbnail in the corner
                small_preview = QtWidgets.QLabel(self)
                small_preview.setPixmap(pixmap)
                small_preview.setStyleSheet("background-color: white; border: 1px solid black;")
                small_preview.setFixedSize(200, 200)
                small_preview.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
                small_preview.show()
                
                # Auto close after 3 seconds
                QtCore.QTimer.singleShot(3000, small_preview.close)
            except Exception as e:
                print(f"Error showing thumbnail: {str(e)}")
            
            # Open the folder so the user can check the screenshot
            self.open_output_folder()
            
        except Exception as e:
            self.status_bar.showMessage(f"Error taking screenshot: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def is_image_black(self, pil_image):
        """Check if a PIL image is all or mostly black"""
        # Convert to numpy array for faster analysis
        img_array = np.array(pil_image)
        
        # Calculate the mean brightness across all channels
        mean_brightness = np.mean(img_array)
        
        # If mean brightness is very low, consider it black
        return mean_brightness < 10
    
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            # Only initiate stop if we're not already stopping
            if not self.is_stopping_recording:
                self.stop_recording()

    def start_recording(self):
        if not self.capture_region:
            self.status_bar.showMessage("Please select a region first")
            return
        
        # Create a timestamp for the filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get preferred output format
        preferred_format = self.output_format_combo.currentText().lower()
        
        # Set filename based on preferred format
        self.video_filename = os.path.join(self.output_dir, f"recording_{timestamp}.{preferred_format}")
        
        # Calculate quality settings
        quality_index = self.video_quality_combo.currentIndex()
        if quality_index == 0:  # Low
            self.codec_quality = 23
        elif quality_index == 1:  # Medium
            self.codec_quality = 18
        else:  # High
            self.codec_quality = 13
        
        try:
            # Get FPS setting
            self.recording_fps = self.fps_spin.value()
            
            # Start recording in a separate thread
            self.is_recording = True
            self.record_btn.setText("Stop Recording")
            self.select_region_btn.setEnabled(False)
            self.take_screenshot_btn.setEnabled(False)
            
            # Start the recording thread
            self.recording_thread = threading.Thread(target=self.record_screen)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            self.status_bar.showMessage(f"Recording started in {preferred_format.upper()} format. Switch to your target window.")
        except Exception as e:
            self.is_recording = False
            self.status_bar.showMessage(f"Error starting recording: {str(e)}")
    
    def stop_recording(self):
        if self.is_recording and not self.is_stopping_recording:
            # Set the stopping flag to prevent multiple stop attempts
            self.is_stopping_recording = True
            
            # Update UI immediately to give feedback
            self.record_btn.setText("Stopping...")
            self.record_btn.setEnabled(False)
            self.status_bar.showMessage("Stopping recording, please wait...")
            
            # Process UI events to update the display
            QtWidgets.QApplication.processEvents()
            
            # Actually stop the recording
            self.is_recording = False
            
            # Wait for recording thread to finish
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=5.0)
            
            # Reset UI
            self.record_btn.setText("Start Recording")
            self.record_btn.setEnabled(True)
            self.select_region_btn.setEnabled(True)
            self.take_screenshot_btn.setEnabled(True)
            
            # Reset flag
            self.is_stopping_recording = False
            
            # Show completion message
            self.status_bar.showMessage(f"Recording saved to {self.video_filename}")
            
            # Open output folder so user can see the video
            self.open_output_folder()
    
    def record_screen(self):
        try:
            # Get region dimensions
            x, y, width, height = self.capture_region
            
            # Ensure even dimensions (required by some codecs)
            width = width if width % 2 == 0 else width - 1
            height = height if height % 2 == 0 else height - 1
            
            # Get preferred format
            preferred_format = self.output_format_combo.currentText().lower()
            
            # Setup codec and output file based on preferred format
            if preferred_format == "mp4":
                # For MP4, we'll record to temp AVI first then convert for quality
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                temp_file = os.path.join(self.output_dir, f"temp_{os.path.basename(self.video_filename)}.avi")
                print(f"Recording to temporary AVI file: {temp_file} (will be converted to MP4)")
            else:
                # For direct AVI output
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                temp_file = self.video_filename
                print(f"Recording directly to AVI file: {temp_file}")
            
            # Create video writer
            out = cv2.VideoWriter(
                temp_file,
                fourcc, 
                self.recording_fps, 
                (width, height)
            )
            
            # Store temp filename for later processing
            self.temp_file = temp_file
            
            # Print debug info
            print(f"Region: {self.capture_region}, using dimensions {width}x{height}")
            print(f"FPS: {self.recording_fps}, Quality: {self.codec_quality}")
            
            # Countdown to recording
            self.status_bar.showMessage("Recording will start in 3 seconds...")
            time.sleep(3)
            
            # Try to import MSS for better multi-monitor support
            try:
                import mss
                use_mss = True
                sct = mss.mss()
                # Define the region to capture
                monitor = {"top": y, "left": x, "width": width, "height": height}
                print("Using MSS for screen capture (better for multi-monitor setups)")
            except ImportError:
                use_mss = False
                print("MSS not available, using PyAutoGUI for capture")
            
            # If scrolling is enabled, perform scrolling during recording
            if self.enable_scrolling_cb.isChecked():
                # Start scrolling in a separate thread
                scroll_thread = threading.Thread(target=self.delayed_scroll)
                scroll_thread.daemon = True
                scroll_thread.start()
            
            # Get start time
            start_time = time.time()
            frame_time = 1.0 / self.recording_fps
            next_frame_time = start_time
            
            # Main recording loop
            frame_count = 0
            while self.is_recording:
                current_time = time.time()
                
                # Maintain consistent FPS
                if current_time >= next_frame_time:
                    # Capture screenshot of the region using the appropriate method
                    if use_mss:
                        # Use MSS for better multi-monitor support
                        sct_img = sct.grab(monitor)
                        # Convert to numpy array directly
                        frame = np.array(sct_img)
                        # Convert BGRA to BGR (remove alpha channel)
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    else:
                        # Fallback to PyAutoGUI
                        img = pyautogui.screenshot(region=(x, y, width, height))
                        # Convert PIL image to OpenCV format
                        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    
                    # Write frame to video
                    out.write(frame)
                    frame_count += 1
                    
                    # Calculate next frame time
                    next_frame_time = start_time + (frame_count + 1) * frame_time
                    
                    # Update UI occasionally
                    if int(current_time) % 2 == 0:
                        # Update status on main thread
                        QtCore.QMetaObject.invokeMethod(
                            self.status_bar, 
                            "showMessage", 
                            QtCore.Qt.QueuedConnection,
                            QtCore.Q_ARG(str, f"Recording: {int(current_time - start_time)}s, {frame_count} frames")
                        )
                else:
                    # Small sleep to prevent CPU hogging
                    time.sleep(0.001)
            
            # Clean up resources
            if use_mss:
                sct.close()
                
            # Release video writer
            out.release()
            print(f"Recording finished with {frame_count} frames captured")
            
            # Process the video based on format
            if preferred_format == "mp4":
                # Convert AVI to MP4 for better compatibility
                self.finalize_video()
            else:
                # AVI is already in final form
                self.status_bar.showMessage(f"Video saved to {self.video_filename}")
            
        except Exception as e:
            self.status_bar.showMessage(f"Error during recording: {str(e)}")
            print(f"Error during recording: {str(e)}")
            import traceback
            traceback.print_exc()
            self.is_recording = False
    
    def finalize_video(self):
        """Convert temporary AVI file to MP4 with proper quality settings"""
        try:
            # Use ffmpeg to convert AVI to MP4 with high quality
            ffmpeg_cmd = f'ffmpeg -i "{self.temp_file}" -c:v libx264 -crf {self.codec_quality} "{self.video_filename}"'
            print(f"Running conversion: {ffmpeg_cmd}")
            result = os.system(ffmpeg_cmd)
            print(f"Conversion completed with result code: {result}")
            
            # Check if conversion was successful
            if os.path.exists(self.video_filename) and os.path.getsize(self.video_filename) > 0:
                # Remove the temporary AVI file
                os.remove(self.temp_file)
                self.status_bar.showMessage(f"Video processed and saved to {self.video_filename}")
                print(f"Conversion successful, temporary file removed, final video at: {self.video_filename}")
            else:
                # If conversion failed, keep the AVI file and rename it to the expected output name
                print(f"Conversion failed, using original AVI file as output")
                # If the video format was supposed to be MP4 but conversion failed, use the AVI file
                if self.video_filename.lower().endswith('.mp4'):
                    # Just rename the temp file to match the expected name (but with .avi extension)
                    final_avi = self.video_filename.replace('.mp4', '.avi')
                    os.rename(self.temp_file, final_avi)
                    self.video_filename = final_avi
                    self.status_bar.showMessage(f"MP4 conversion failed, saved as AVI instead: {self.video_filename}")
                else:
                    # This shouldn't happen, but just in case
                    self.status_bar.showMessage(f"Video saved at {self.temp_file}")
        except Exception as e:
            self.status_bar.showMessage(f"Error converting video: {str(e)}")
            print(f"Error converting video: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def browse_output_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Output Folder", self.output_dir
        )
        if folder:
            self.output_dir = folder
            self.output_path_edit.setText(folder)
            self.output_path_label.setText(f"Output Path: {folder}")
    
    def open_output_folder(self):
        # Open the output folder in file explorer
        if os.path.exists(self.output_dir):
            os.startfile(self.output_dir)
        else:
            self.status_bar.showMessage(f"Output folder does not exist: {self.output_dir}")
    
    def save_settings(self):
        # Here you would save settings to a file
        # This is a simple version that just shows a message
        self.status_bar.showMessage("Settings saved")
    
    def load_settings(self):
        # Here you would load settings from a file
        # This is a simple version that just keeps defaults
        pass
    
    def smooth_move(self, x, y, duration=1):
        """Move mouse smoothly to the coordinates"""
        pyautogui.moveTo(x, y, duration=duration)
    
    def smooth_scroll(self, total_scroll, duration=3.0, step_size=5):
        """
        Perform smooth scrolling with fine control over speed
        
        Args:
            total_scroll: Total amount to scroll (negative for down)
            duration: Total time the scrolling should take (in seconds)
            step_size: Size of each individual scroll step (smaller = smoother)
        """
        # Number of steps based on total scroll and step size
        steps = abs(total_scroll) // step_size
        if steps == 0:
            steps = 1
        
        # Calculate delay between steps
        delay = duration / steps
        
        # Direction (negative = down, positive = up)
        direction = -1 if total_scroll < 0 else 1
        
        print(f"Smoothly scrolling {total_scroll} over {duration} seconds... Press ESC to stop.")
        self.status_bar.showMessage(f"Scrolling... Press ESC to stop.")
        
        # Try to use PyAutoGUI directly for keyboard detection
        try:
            from pynput import keyboard
            
            # Flag to track if ESC was pressed
            esc_pressed = [False]  # Using list for mutable state in the callback
            
            # Setup keyboard listener to detect ESC key
            def on_press(key):
                try:
                    if key == keyboard.Key.esc:
                        print("ESC key detected, stopping scroll")
                        esc_pressed[0] = True
                        return False  # Stop listener
                except:
                    pass
                return True
                
            # Start keyboard listener
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
            
            # Perform the scrolling in steps
            for i in range(steps):
                # Check if ESC was pressed
                if esc_pressed[0]:
                    print("Stopping scroll due to ESC key")
                    self.status_bar.showMessage("Scrolling stopped by ESC key")
                    break
                    
                # Perform scroll step
                pyautogui.scroll(direction * step_size)
                time.sleep(delay)
                
                # Update progress every 10 steps
                if i % 10 == 0:
                    print(f"Scrolling progress: {i}/{steps} steps")
                    
            # Clean up listener
            if listener.is_alive():
                listener.stop()
                
        except ImportError:
            # If pynput is not available, fallback to basic scrolling
            print("WARNING: pynput not available. Install with 'pip install pynput' to enable ESC to stop scrolling.")
            
            # Perform the scrolling in steps without ESC detection
            for i in range(steps):
                # Perform scroll step
                pyautogui.scroll(direction * step_size)
                time.sleep(delay)
                
                # Update progress every 10 steps
                if i % 10 == 0:
                    print(f"Scrolling progress: {i}/{steps} steps")
                    
        self.status_bar.showMessage("Scrolling completed")
    
    def delayed_scroll(self):
        """Performs scrolling after a short delay (used during recording)"""
        # Give a moment for user to position mouse manually
        print("Waiting 3 seconds before scrolling...")
        self.status_bar.showMessage("Waiting 3 seconds before scrolling... Please position your mouse over the target window.")
        time.sleep(3)
        
        # Log what we're about to do
        print(f"Starting scrolling with amount={self.scroll_amount_spin.value()}, duration={self.scroll_duration_spin.value()}")
        
        try:
            # Get scroll parameters from UI
            scroll_amount = self.scroll_amount_spin.value()
            scroll_duration = self.scroll_duration_spin.value()
            scroll_step = self.scroll_step_spin.value()
            
            # Update UI to show we're scrolling
            QtCore.QMetaObject.invokeMethod(
                self.status_bar, 
                "showMessage", 
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, f"Recording: Scrolling {abs(scroll_amount)} units... Press ESC to stop.")
            )
            
            # Force UI to update before we start scrolling
            QtWidgets.QApplication.processEvents()
            
            # Calculate steps and delay to maintain the desired duration
            steps = abs(scroll_amount) // scroll_step
            if steps == 0:
                steps = 1
            
            delay = scroll_duration / steps
            direction = -1 if scroll_amount < 0 else 1
            
            print(f"Executing {steps} scroll steps with delay {delay}s")
            
            # Flag to track if scrolling should continue
            self.is_scrolling = True
            
            # Try to use pynput for keyboard detection
            try:
                from pynput import keyboard
                
                # Flag to track if ESC was pressed
                esc_pressed = [False]  # Using list for mutable state in the callback
                
                # Setup keyboard listener to detect ESC key
                def on_press(key):
                    try:
                        if key == keyboard.Key.esc:
                            print("ESC key detected, stopping scroll during recording")
                            esc_pressed[0] = True
                            return False  # Stop listener
                    except:
                        pass
                    return True
                    
                # Start keyboard listener
                listener = keyboard.Listener(on_press=on_press)
                listener.start()
                
                # Perform the scroll directly
                for i in range(steps):
                    # Check if ESC was pressed
                    if esc_pressed[0]:
                        print("Stopping scroll due to ESC key")
                        QtCore.QMetaObject.invokeMethod(
                            self.status_bar, 
                            "showMessage", 
                            QtCore.Qt.QueuedConnection,
                            QtCore.Q_ARG(str, "Scrolling stopped by ESC key")
                        )
                        break
                    
                    # Perform scroll step
                    pyautogui.scroll(direction * scroll_step)
                    time.sleep(delay)
                    
                    # Update progress every 10 steps
                    if i % 10 == 0:
                        print(f"Scrolling progress: {i}/{steps} steps")
                
                # Clean up listener
                if listener.is_alive():
                    listener.stop()
                    
            except ImportError:
                # If pynput is not available, use simpler method without ESC detection
                print("WARNING: pynput not available. Install with 'pip install pynput' to enable ESC to stop scrolling.")
                
                # Perform the scroll directly without ESC detection
                for i in range(steps):
                    # Perform scroll step
                    pyautogui.scroll(direction * scroll_step)
                    time.sleep(delay)
                    
                    # Update progress every 10 steps
                    if i % 10 == 0:
                        print(f"Scrolling progress: {i}/{steps} steps")
    
            self.is_scrolling = False
            print("Scrolling completed or stopped")
    
        except Exception as e:
            self.is_scrolling = False
            print(f"Error during scrolling: {str(e)}")
            import traceback
            traceback.print_exc()

# Run the application
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for consistent look
    window = MarketingScreenCaptureTool()
    window.show()
    sys.exit(app.exec_())