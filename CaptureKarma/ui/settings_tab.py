"""
Settings tab UI component for the Marketing Screen Capture Tool
"""
from PyQt5 import QtWidgets, QtCore


class SettingsTab(QtWidgets.QWidget):
    """Tab for application settings"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
        # Setup the UI components
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the settings tab UI components"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Video settings
        self.setup_video_settings(layout)
        
        # Output settings
        self.setup_output_settings(layout)
        
        # Add save settings button
        save_btn = QtWidgets.QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        # Add spacer at the bottom
        layout.addStretch()
    
    def setup_video_settings(self, parent_layout):
        """Setup video settings UI"""
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
        
        parent_layout.addWidget(video_group)
    
    def setup_output_settings(self, parent_layout):
        """Setup output settings UI"""
        output_group = QtWidgets.QGroupBox("Output Settings")
        output_layout = QtWidgets.QVBoxLayout(output_group)
        
        path_layout = QtWidgets.QHBoxLayout()
        self.output_path_edit = QtWidgets.QLineEdit(self.parent.output_dir)
        self.output_path_edit.setReadOnly(True)
        path_layout.addWidget(self.output_path_edit)
        
        browse_btn = QtWidgets.QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_output_folder)
        path_layout.addWidget(browse_btn)
        
        output_layout.addLayout(path_layout)
        
        parent_layout.addWidget(output_group)
    
    def browse_output_folder(self):
        """Browse for output folder location"""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Output Folder", self.parent.output_dir
        )
        if folder:
            self.parent.output_dir = folder
            self.output_path_edit.setText(folder)
            
            # Update the label in the capture tab
            if hasattr(self.parent, 'capture_tab') and hasattr(self.parent.capture_tab, 'output_path_label'):
                self.parent.capture_tab.output_path_label.setText(f"Output Path: {folder}")
    
    def save_settings(self):
        """Save application settings"""
        # Here you would save settings to a file
        self.parent.status_bar.showMessage("Settings saved")