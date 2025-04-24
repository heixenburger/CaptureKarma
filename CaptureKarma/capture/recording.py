"""
Video recording functionality for the CaptureKarma Screen Capture Tool
"""
import os
import time
import datetime
import threading
import cv2
import numpy as np
import pyautogui
from PIL import Image

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False


class VideoRecorder:
    """Handles video recording functionality"""
    
    def __init__(self, parent):
        self.parent = parent
        self.is_recording = False
        self.is_stopping_recording = False
        self.recording_thread = None
        
        # Variables for recording state
        self.video_filename = None
        self.temp_file = None
        self.recording_fps = 30
        self.codec_quality = 18  # Default medium quality
    
    def start_recording(self, region, output_dir, fps=30, quality_index=2, 
                        output_format="mp4", scrolling_enabled=False, 
                        scroll_amount=0, scroll_duration=0, scroll_step=5):
        """
        Start recording the selected region
        
        Args:
            region: Tuple (x, y, width, height) defining the region to capture
            output_dir: Directory to save the recording
            fps: Frames per second for the recording
            quality_index: Quality index (0=low, 1=medium, 2=high)
            output_format: Output format ("mp4" or "avi")
            scrolling_enabled: Whether to perform scrolling during recording
            scroll_amount: Amount to scroll (negative for down, positive for up)
            scroll_duration: Duration of scrolling in seconds
            scroll_step: Size of each scroll step (smaller = smoother)
        """
        if not region:
            self.parent.parent.status_bar.showMessage("Please select a region first")
            return
        
        # Create a timestamp for the filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Set filename based on preferred format
        self.video_filename = os.path.join(output_dir, f"recording_{timestamp}.{output_format}")
        
        # Calculate quality settings
        if quality_index == 0:  # Low
            self.codec_quality = 23
        elif quality_index == 1:  # Medium
            self.codec_quality = 18
        else:  # High
            self.codec_quality = 13
        
        try:
            # Get FPS setting
            self.recording_fps = fps
            
            # Store parameters for potential scrolling
            self.region = region
            self.scrolling_enabled = scrolling_enabled
            self.scroll_amount = scroll_amount
            self.scroll_duration = scroll_duration
            self.scroll_step = scroll_step
            
            # Set recording flag
            self.is_recording = True
            
            # Start the recording thread
            self.recording_thread = threading.Thread(target=self._record_screen)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            self.parent.parent.status_bar.showMessage(
                f"Recording started in {output_format.upper()} format. Switch to your target window."
            )
        except Exception as e:
            self.is_recording = False
            self.parent.parent.status_bar.showMessage(f"Error starting recording: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def stop_recording(self):
        """Stop the recording and save the video file"""
        if self.is_recording and not self.is_stopping_recording:
            # Set the stopping flag to prevent multiple stop attempts
            self.is_stopping_recording = True
            
            # Update UI
            self.parent.parent.status_bar.showMessage("Stopping recording, please wait...")
            
            # Actually stop the recording
            self.is_recording = False
            
            # Wait for recording thread to finish
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=5.0)
            
            # Reset flag
            self.is_stopping_recording = False
            
            # Show completion message
            self.parent.parent.status_bar.showMessage(f"Recording saved to {self.video_filename}")
            
            # Open output folder so user can see the video
            self.parent.parent.open_output_folder()
    
    def _record_screen(self):
        """Record the screen region in a background thread"""
        try:
            # Get region dimensions
            x, y, width, height = self.region
            
            # Ensure even dimensions (required by some codecs)
            width = width if width % 2 == 0 else width - 1
            height = height if height % 2 == 0 else height - 1
            
            # Get preferred format
            preferred_format = os.path.splitext(self.video_filename)[1].lower().lstrip('.')
            
            # Setup codec and output file based on preferred format
            if preferred_format == "mp4":
                # For MP4, we'll record to temp AVI first then convert for quality
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                temp_file = os.path.join(os.path.dirname(self.video_filename), 
                                        f"temp_{os.path.basename(self.video_filename)}.avi")
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
            print(f"Region: {self.region}, using dimensions {width}x{height}")
            print(f"FPS: {self.recording_fps}, Quality: {self.codec_quality}")
            
            # Countdown to recording
            self.parent.parent.status_bar.showMessage("Recording will start in 3 seconds...")
            time.sleep(3)
            
            # Setup MSS for capture if available
            if MSS_AVAILABLE:
                sct = mss.mss()
                monitor = {"top": y, "left": x, "width": width, "height": height}
                use_mss = True
                print("Using MSS for screen capture (better for multi-monitor setups)")
            else:
                use_mss = False
                print("MSS not available, using PyAutoGUI for capture")
            
            # If scrolling is enabled, start scrolling in a separate thread
            if self.scrolling_enabled:
                self._start_scrolling_thread()
            
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
                    if frame_count % 30 == 0:  # Update every 30 frames
                        elapsed = int(current_time - start_time)
                        self.parent.parent.status_bar.showMessage(
                            f"Recording: {elapsed}s, {frame_count} frames"
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
                self._finalize_video()
            else:
                # AVI is already in final form
                self.parent.parent.status_bar.showMessage(f"Video saved to {self.video_filename}")
            
        except Exception as e:
            self.parent.parent.status_bar.showMessage(f"Error during recording: {str(e)}")
            print(f"Error during recording: {str(e)}")
            import traceback
            traceback.print_exc()
            self.is_recording = False
    
    def _start_scrolling_thread(self):
        """Start a thread to handle scrolling during recording"""
        from CaptureKarma.utils.scrolling import ScrollingManager
        
        # Create scrolling manager
        scrolling_manager = ScrollingManager()
        
        # Start scrolling in a separate thread
        scroll_thread = threading.Thread(
            target=scrolling_manager.delayed_scroll,
            args=(
                self.scroll_amount,
                self.scroll_duration,
                self.scroll_step,
                lambda msg: self.parent.parent.status_bar.showMessage(msg)
            )
        )
        scroll_thread.daemon = True
        scroll_thread.start()
    
    def _finalize_video(self):
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
                self.parent.parent.status_bar.showMessage(f"Video processed and saved to {self.video_filename}")
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
                    self.parent.parent.status_bar.showMessage(
                        f"MP4 conversion failed, saved as AVI instead: {self.video_filename}"
                    )
                else:
                    # This shouldn't happen, but just in case
                    self.parent.parent.status_bar.showMessage(f"Video saved at {self.temp_file}")
        except Exception as e:
            self.parent.parent.status_bar.showMessage(f"Error converting video: {str(e)}")
            print(f"Error converting video: {str(e)}")
            import traceback
            traceback.print_exc()