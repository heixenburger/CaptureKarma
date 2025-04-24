"""
Capture tab UI component for the CaptureKarma Screen Capture Tool
"""
import os
from PyQt5 import QtWidgets, QtCore, QtGui

from CaptureKarma.capture.region import RegionSelector
from CaptureKarma.capture.screenshot import ScreenshotCapture
from CaptureKarma.capture.recording import VideoRecorder
from CaptureKarma.utils.scrolling import ScrollingManager


class CaptureTab(QtWidgets.QWidget):
    """Tab for capture functionality including screenshots and recording"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.capture_region = None
        
        # Create helper classes
        self.region_selector = RegionSelector(self)
        self.screenshot_capture = ScreenshotCapture(self)
        self.video_recorder = VideoRecorder(self)
        self.scrolling_manager = ScrollingManager()
        
        # Setup the UI components
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the capture tab UI components"""
        layout = QtWidgets.QVBoxLayout(self)
        
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
        self.setup_scrolling_options(layout)
        
        # Output info
        self.setup_output_info(layout)
    
    def setup_scrolling_options(self, parent_layout):
        """Setup scrolling options UI"""
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
        parent_layout.addWidget(scroll_group)
    
    def setup_output_info(self, parent_layout):
        """Setup output information UI"""
        output_group = QtWidgets.QGroupBox("Output Information")
        output_layout = QtWidgets.QVBoxLayout(output_group)
        
        self.output_path_label = QtWidgets.QLabel(f"Output Path: {self.parent.output_dir}")
        output_layout.addWidget(self.output_path_label)
        
        self.open_folder_btn = QtWidgets.QPushButton("Open Output Folder")
        self.open_folder_btn.clicked.connect(self.parent.open_output_folder)
        output_layout.addWidget(self.open_folder_btn)
        
        parent_layout.addWidget(output_group)
    
    def select_capture_region(self):
        """Open the region selection dialog"""
        self.capture_region = self.region_selector.select_region()
        
        if self.capture_region:
            # Enable capture buttons
            self.take_screenshot_btn.setEnabled(True)
            self.record_btn.setEnabled(True)
    
    def take_screenshot(self):
        """Capture a screenshot of the selected region"""
        if not self.capture_region:
            self.parent.status_bar.showMessage("Please select a region first")
            return
        
        # Get scrolling options
        scrolling_enabled = self.enable_scrolling_cb.isChecked()
        scroll_amount = self.scroll_amount_spin.value() if scrolling_enabled else 0
        scroll_duration = self.scroll_duration_spin.value() if scrolling_enabled else 0
        scroll_step = self.scroll_step_spin.value() if scrolling_enabled else 0
        
        # Take the screenshot
        self.screenshot_capture.take_screenshot(
            self.capture_region,
            self.parent.output_dir,
            scrolling_enabled=scrolling_enabled,
            scroll_amount=scroll_amount,
            scroll_duration=scroll_duration,
            scroll_step=scroll_step
        )
    
    def toggle_recording(self):
        """Start or stop video recording"""
        if not self.video_recorder.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start video recording"""
        if not self.capture_region:
            self.parent.status_bar.showMessage("Please select a region first")
            return
        
        # Get settings from the settings tab
        settings_tab = self.parent.settings_tab
        fps = settings_tab.fps_spin.value()
        quality_index = settings_tab.video_quality_combo.currentIndex()
        output_format = settings_tab.output_format_combo.currentText().lower()
        
        # Get scrolling options
        scrolling_enabled = self.enable_scrolling_cb.isChecked()
        scroll_amount = self.scroll_amount_spin.value() if scrolling_enabled else 0
        scroll_duration = self.scroll_duration_spin.value() if scrolling_enabled else 0
        scroll_step = self.scroll_step_spin.value() if scrolling_enabled else 0
        
        # Start recording
        self.video_recorder.start_recording(
            self.capture_region,
            self.parent.output_dir,
            fps=fps,
            quality_index=quality_index,
            output_format=output_format,
            scrolling_enabled=scrolling_enabled,
            scroll_amount=scroll_amount,
            scroll_duration=scroll_duration,
            scroll_step=scroll_step
        )
        
        # Update UI
        self.record_btn.setText("Stop Recording")
        self.select_region_btn.setEnabled(False)
        self.take_screenshot_btn.setEnabled(False)
    
    def stop_recording(self):
        """Stop video recording"""
        self.video_recorder.stop_recording()
        
        # Reset UI
        self.record_btn.setText("Start Recording")
        self.select_region_btn.setEnabled(True)
        self.take_screenshot_btn.setEnabled(True)
    
    def update_preview(self, pixmap):
        """Update the preview with a captured image"""
        # Scale pixmap to fit the preview label while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.preview_label.width(), 
            self.preview_label.height(),
            QtCore.Qt.KeepAspectRatio
        )
        
        # Set the pixmap to the label
        self.preview_label.setPixmap(scaled_pixmap)