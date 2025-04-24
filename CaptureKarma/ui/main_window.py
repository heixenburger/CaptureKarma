"""
Main window UI for the CaptureKarma Screen Capture Tool
"""
import os
import sys
from PyQt5 import QtWidgets, QtCore

from CaptureKarma.ui.capture_tab import CaptureTab
from CaptureKarma.ui.settings_tab import SettingsTab
from CaptureKarma.ui.about_tab import AboutTab


class MarketingScreenCaptureTool(QtWidgets.QMainWindow):
    """Main application window for the screen capture tool"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CaptureKarma Screen Capture Tool")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize variables
        self.output_dir = os.path.join(os.path.expanduser("~"), "Documents", "CaptureKarma")
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Main layout
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        
        # Create tabs
        self.tabs = QtWidgets.QTabWidget()
        self.capture_tab = CaptureTab(self)
        self.settings_tab = SettingsTab(self)
        self.about_tab = AboutTab(self)
        
        self.tabs.addTab(self.capture_tab, "Capture")
        self.tabs.addTab(self.settings_tab, "Settings")
        self.tabs.addTab(self.about_tab, "About")
        
        main_layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
        # Load settings
        self.load_settings()
    
    def load_settings(self):
        """Load application settings"""
        # Here you would load settings from a file
        pass
    
    def open_output_folder(self):
        """Open the output folder in file explorer"""
        if os.path.exists(self.output_dir):
            os.startfile(self.output_dir)
        else:
            self.status_bar.showMessage(f"Output folder does not exist: {self.output_dir}")
    
    def set_output_dir(self, directory):
        """Set the output directory"""
        self.output_dir = directory