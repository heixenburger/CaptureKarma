"""
About tab UI component for the CaptureKarma Screen Capture Tool
"""
from PyQt5 import QtWidgets, QtCore, QtGui


class AboutTab(QtWidgets.QWidget):
    """Tab displaying information about the application"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
        # Setup the UI components
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the about tab UI components"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Add logo/title
        title_layout = QtWidgets.QHBoxLayout()
        
        # App logo - can be replaced with an actual logo image later
        logo_label = QtWidgets.QLabel()
        logo_pixmap = self._create_app_logo(128, 128)
        logo_label.setPixmap(logo_pixmap)
        title_layout.addWidget(logo_label)
        
        # Title and version
        title_widget = QtWidgets.QWidget()
        title_inner_layout = QtWidgets.QVBoxLayout(title_widget)
        
        app_name_label = QtWidgets.QLabel("CaptureKarma")
        app_name_label.setStyleSheet("font-size: 24pt; font-weight: bold;")
        title_inner_layout.addWidget(app_name_label)
        
        app_description = QtWidgets.QLabel("Screen Capture Tool")
        app_description.setStyleSheet("font-size: 14pt;")
        title_inner_layout.addWidget(app_description)
        
        version_label = QtWidgets.QLabel("Version 0.1.0")
        version_label.setStyleSheet("font-style: italic; color: #666;")
        title_inner_layout.addWidget(version_label)
        
        title_inner_layout.addStretch()
        title_layout.addWidget(title_widget)
        title_layout.addStretch(1)
        
        layout.addLayout(title_layout)
        
        # Add a line separator
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)
        
        # Story content using a scrollable text area
        story_group = QtWidgets.QGroupBox("The Story Behind CaptureKarma")
        story_layout = QtWidgets.QVBoxLayout(story_group)
        
        story_text = QtWidgets.QTextEdit()
        story_text.setReadOnly(True)
        story_text.setHtml(self._get_story_html())
        story_layout.addWidget(story_text)
        
        layout.addWidget(story_group)
        
        # Creator information section
        creator_group = QtWidgets.QGroupBox("About the Creator")
        creator_layout = QtWidgets.QVBoxLayout(creator_group)
        
        creator_text = QtWidgets.QLabel(
            "Created by a perfectionist who wasn't satisfied with jerky scrolling in marketing videos.\n"
            "Developed as a hobby project while working at Paracosma."
        )
        creator_text.setWordWrap(True)
        creator_layout.addWidget(creator_text)
        
        layout.addWidget(creator_group)
        
        # License section
        license_group = QtWidgets.QGroupBox("License")
        license_layout = QtWidgets.QVBoxLayout(license_group)
        
        license_text = QtWidgets.QLabel("This software is released under the \"Don't Be A Dick\" Public License.\nDo whatever you want with the code, just don't be a dick about it.")
        license_text.setWordWrap(True)
        license_layout.addWidget(license_text)
        
        layout.addWidget(license_group)
        
        # Add some padding at the bottom
        layout.addStretch()
    
    def _create_app_logo(self, width, height):
        """Create a simple app logo as a colored shape"""
        pixmap = QtGui.QPixmap(width, height)
        pixmap.fill(QtCore.Qt.transparent)
        
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw a gradient background
        gradient = QtGui.QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, QtGui.QColor(60, 120, 200))
        gradient.setColorAt(1, QtGui.QColor(30, 60, 160))
        painter.setBrush(gradient)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(2, 2, width-4, height-4, 15, 15)
        
        # Draw a camera shape
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 3))
        painter.setBrush(QtGui.QColor(220, 220, 220, 180))
        
        # Camera body
        camera_body = QtCore.QRect(width//4, height//3, width//2, height//3)
        painter.drawRoundedRect(camera_body, 8, 8)
        
        # Camera lens
        lens_center = QtCore.QPoint(width//2, height//2)
        lens_radius = min(width, height) // 6
        painter.drawEllipse(lens_center, lens_radius, lens_radius)
        
        # Small inner lens
        painter.setBrush(QtGui.QColor(180, 200, 255))
        painter.drawEllipse(lens_center, lens_radius//2, lens_radius//2)
        
        # Camera flash
        flash_rect = QtCore.QRect(width//4 + width//10, height//3 - height//10, width//10, height//20)
        painter.drawRoundedRect(flash_rect, 2, 2)
        
        painter.end()
        return pixmap
    
    def _get_story_html(self):
        """Get the HTML formatted story text"""
        return """
        <p>I developed CaptureKarma as a hobby project while working at Paracosma. Our marketing team 
        frequently needed to create product videos and demonstrations, but achieving perfectly smooth 
        scrolling manually was challenging and often produced inconsistent results.</p>
        
        <p>As a perfectionist, I found myself frustrated with the small imperfections in these 
        marketing materials. The jerky movements and inconsistent speeds when scrolling manually 
        through product pages or demonstrations didn't reflect the quality of our work.</p>
        
        <p>This tool was born from my desire to solve this problem once and for all - creating a 
        utility that could produce pixel-perfect scrolling captures every time.</p>
        """