"""
Scrolling utilities for the CaptureKarma Screen Capture Tool
"""
import time
import pyautogui

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class ScrollingManager:
    """Manages smooth scrolling functionality"""
    
    def __init__(self):
        self.is_scrolling = False
    
    def smooth_move(self, x, y, duration=1.0):
        """Move mouse smoothly to the coordinates"""
        pyautogui.moveTo(x, y, duration=duration)
    
    def smooth_scroll(self, total_scroll, duration=3.0, step_size=5, status_callback=None):
        """
        Perform smooth scrolling with fine control over speed
        
        Args:
            total_scroll: Total amount to scroll (negative for down)
            duration: Total time the scrolling should take (in seconds)
            step_size: Size of each individual scroll step (smaller = smoother)
            status_callback: Optional callback function to report status messages
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
        if status_callback:
            status_callback("Scrolling... Press ESC to stop.")
        
        # Flag to track if ESC was pressed
        esc_pressed = [False]  # Using list for mutable state in the callback
        
        # Try to use PyNput for keyboard detection
        if PYNPUT_AVAILABLE:
            self._scroll_with_esc_detection(steps, direction, step_size, delay, esc_pressed, status_callback)
        else:
            self._scroll_basic(steps, direction, step_size, delay, status_callback)
    
    def _scroll_with_esc_detection(self, steps, direction, step_size, delay, esc_pressed, status_callback=None):
        """Perform scrolling with ESC key detection to stop"""
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
                if status_callback:
                    status_callback("Scrolling stopped by ESC key")
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
    
    def _scroll_basic(self, steps, direction, step_size, delay, status_callback=None):
        """Perform basic scrolling without ESC detection"""
        print("WARNING: pynput not available. Install with 'pip install pynput' to enable ESC to stop scrolling.")
        
        # Perform the scrolling in steps without ESC detection
        for i in range(steps):
            # Perform scroll step
            pyautogui.scroll(direction * step_size)
            time.sleep(delay)
            
            # Update progress every 10 steps
            if i % 10 == 0:
                print(f"Scrolling progress: {i}/{steps} steps")
                
        if status_callback:
            status_callback("Scrolling completed")
    
    def delayed_scroll(self, scroll_amount, scroll_duration, scroll_step, status_callback=None):
        """Perform scrolling after a short delay (useful during recording)"""
        # Give a moment for user to position mouse manually
        print("Waiting 3 seconds before scrolling...")
        if status_callback:
            status_callback("Waiting 3 seconds before scrolling... Please position your mouse over the target window.")
        time.sleep(3)
        
        # Log what we're about to do
        print(f"Starting scrolling with amount={scroll_amount}, duration={scroll_duration}")
        
        # Set flag to indicate we're scrolling
        self.is_scrolling = True
        
        try:
            if status_callback:
                status_callback(f"Recording: Scrolling {abs(scroll_amount)} units... Press ESC to stop.")
            
            # Perform the scroll
            self.smooth_scroll(scroll_amount, scroll_duration, scroll_step, status_callback)
                
            self.is_scrolling = False
            print("Scrolling completed or stopped")
        
        except Exception as e:
            self.is_scrolling = False
            print(f"Error during scrolling: {str(e)}")
            import traceback
            traceback.print_exc()