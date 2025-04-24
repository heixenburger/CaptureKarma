#!/usr/bin/env python3
"""
Main entry point for the CaptureKarma Screen Capture Tool.

This tool allows capturing screenshots and recording videos of selected screen regions,
with support for scrolling and multiple monitors.
"""
import sys
from PyQt5 import QtWidgets

from CaptureKarma.ui.main_window import MarketingScreenCaptureTool


def main():
    """Main entry point function"""
    # Use PyQt5's fusion style for a more modern look
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Create and show the main window
    window = MarketingScreenCaptureTool()
    window.show()
    
    # Enter the application's main event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
