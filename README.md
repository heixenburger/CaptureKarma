# CaptureKarma Screen Capture Tool

A comprehensive screen capture tool for creating marketing materials, tutorials, and demonstrations.

## The Story Behind CaptureKarma

I developed CaptureKarma as a hobby project while working at Paracosma. Our marketing team frequently needed to create product videos and demonstrations, but achieving perfectly smooth scrolling manually was challenging and often produced inconsistent results.

As a perfectionist, I found myself frustrated with the small imperfections in these marketing materials. The jerky movements and inconsistent speeds when scrolling manually through product pages or demonstrations didn't reflect the quality of our work. This tool was born from my desire to solve this problem once and for all - creating a utility that could produce pixel-perfect scrolling captures every time.

## Features

-   **Region Selection**: Capture specific windows or entire monitors
-   **Screenshot Capture**: Take screenshots with a single click
-   **Video Recording**: Record high-quality videos of screen activity
-   **Scrolling Support**: Automatically scroll during capture for long pages
-   **Multiple Monitor Support**: Works with multi-monitor setups
-   **Flexible Output**: Save in various formats including PNG, MP4, and AVI

## Installation

### Prerequisites

-   Python 3.8 or higher
-   FFmpeg (for MP4 video conversion)

### Setup

1. Clone the repository:

    ```
    git clone https://github.com/yourusername/capturekarma-screen-capture.git
    cd capturekarma-screen-capture
    ```

2. Create and activate a virtual environment:

    ```
    python -m venv .venv
    # On Windows:
    .venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate
    ```

3. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage

Run the application:

```
python main.py
```

### Basic Workflow

1. Select a region to capture (window or monitor)
2. Adjust settings as needed
3. Take a screenshot or start recording
4. For scrolling captures, enable the scrolling option and set parameters

## Project Structure

```
capturekarma-screen-capture/
├── main.py                      # Entry point
├── pyproject.toml               # Project configuration
├── requirements.txt             # Dependencies list
├── README.md                    # Documentation
└── CaptureKarma/                # Main package
    ├── ui/                      # UI-related code
    │   ├── main_window.py       # Main window UI
    │   ├── capture_tab.py       # Capture tab UI components
    │   └── settings_tab.py      # Settings tab UI components
    ├── capture/                 # Capture functionality
    │   ├── screenshot.py        # Screenshot logic
    │   ├── recording.py         # Video recording logic
    │   └── region.py            # Region selection logic
    └── utils/                   # Utility functions
        ├── image_processing.py  # Image processing utilities
        └── scrolling.py         # Scrolling utilities
```

## License

["Don't Be A Dick" Public License](LICENSE)

This project is licensed under the DBAD license - do whatever you want with the code, just don't be a dick about it.
