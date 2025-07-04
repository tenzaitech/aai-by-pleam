import pyautogui
import time
import cv2
import numpy as np
from PIL import Image, ImageGrab
import os
from typing import Tuple, List, Dict, Optional

class MouseKeyboardController:
    def __init__(self, safety_delay: float = 0.1):
        """Initialize Mouse & Keyboard Controller"""
        # Set safety settings
        pyautogui.FAILSAFE = True  # Move mouse to corner to stop
        pyautogui.PAUSE = safety_delay
        
        # Get screen size
        self.screen_width, self.screen_height = pyautogui.size()
        
        print(f"✅ Mouse & Keyboard Controller initialized")
        print(f"📱 Screen size: {self.screen_width}x{self.screen_height}")
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        return pyautogui.position()
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> bool:
        """Move mouse to specific coordinates"""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            print(f"✅ Mouse moved to ({x}, {y})")
            return True
        except Exception as e:
            print(f"❌ Mouse movement failed: {str(e)}")
            return False
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, 
              button: str = 'left', clicks: int = 1, interval: float = 0.1) -> bool:
        """Click at current position or specified coordinates"""
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
            else:
                pyautogui.click(clicks=clicks, interval=interval, button=button)
            
            print(f"✅ Clicked {button} button {clicks} time(s)")
            return True
        except Exception as e:
            print(f"❌ Click failed: {str(e)}")
            return False
    
    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Double click at position"""
        return self.click(x, y, clicks=2)
    
    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Right click at position"""
        return self.click(x, y, button='right')
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
             duration: float = 1.0) -> bool:
        """Drag mouse from start to end position"""
        try:
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
            print(f"✅ Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            return True
        except Exception as e:
            print(f"❌ Drag failed: {str(e)}")
            return False
    
    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Scroll up (positive) or down (negative)"""
        try:
            if x is not None and y is not None:
                pyautogui.scroll(clicks, x=x, y=y)
            else:
                pyautogui.scroll(clicks)
            
            direction = "up" if clicks > 0 else "down"
            print(f"✅ Scrolled {direction} {abs(clicks)} clicks")
            return True
        except Exception as e:
            print(f"❌ Scroll failed: {str(e)}")
            return False
    
    def type_text(self, text: str, interval: float = 0.1) -> bool:
        """Type text with specified interval"""
        try:
            pyautogui.typewrite(text, interval=interval)
            print(f"✅ Typed text: {text}")
            return True
        except Exception as e:
            print(f"❌ Type text failed: {str(e)}")
            return False
    
    def press_key(self, key: str) -> bool:
        """Press a single key"""
        try:
            pyautogui.press(key)
            print(f"✅ Pressed key: {key}")
            return True
        except Exception as e:
            print(f"❌ Press key failed: {str(e)}")
            return False
    
    def hotkey(self, *keys) -> bool:
        """Press combination of keys"""
        try:
            pyautogui.hotkey(*keys)
            print(f"✅ Pressed hotkey: {'+'.join(keys)}")
            return True
        except Exception as e:
            print(f"❌ Hotkey failed: {str(e)}")
            return False
    
    def find_image_on_screen(self, image_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """Find image on screen and return coordinates"""
        try:
            if not os.path.exists(image_path):
                print(f"❌ Image file not found: {image_path}")
                return None
            
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                print(f"✅ Found image at: {center}")
                return center
            else:
                print(f"❌ Image not found on screen")
                return None
                
        except Exception as e:
            print(f"❌ Find image failed: {str(e)}")
            return None
    
    def click_image(self, image_path: str, confidence: float = 0.8) -> bool:
        """Find and click on image"""
        try:
            coords = self.find_image_on_screen(image_path, confidence)
            if coords:
                return self.click(coords[0], coords[1])
            return False
        except Exception as e:
            print(f"❌ Click image failed: {str(e)}")
            return False
    
    def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None, 
                       save_path: str = "screenshot.png") -> bool:
        """Take screenshot of entire screen or specific region"""
        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            screenshot.save(save_path)
            print(f"✅ Screenshot saved: {save_path}")
            return True
        except Exception as e:
            print(f"❌ Screenshot failed: {str(e)}")
            return False
    
    def wait_for_image(self, image_path: str, timeout: float = 10.0, 
                      confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """Wait for image to appear on screen"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                coords = self.find_image_on_screen(image_path, confidence)
                if coords:
                    print(f"✅ Image appeared after {time.time() - start_time:.2f}s")
                    return coords
                time.sleep(0.5)
            
            print(f"❌ Image not found within {timeout}s")
            return None
        except Exception as e:
            print(f"❌ Wait for image failed: {str(e)}")
            return None
    
    def get_pixel_color(self, x: int, y: int) -> Optional[Tuple[int, int, int]]:
        """Get color of pixel at coordinates"""
        try:
            color = pyautogui.pixel(x, y)
            print(f"✅ Pixel color at ({x}, {y}): RGB{color}")
            return color
        except Exception as e:
            print(f"❌ Get pixel color failed: {str(e)}")
            return None
    
    def wait_for_color_change(self, x: int, y: int, target_color: Tuple[int, int, int], 
                            timeout: float = 10.0, tolerance: int = 10) -> bool:
        """Wait for pixel color to change to target color"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                current_color = self.get_pixel_color(x, y)
                if current_color:
                    # Check if color matches within tolerance
                    if all(abs(current_color[i] - target_color[i]) <= tolerance for i in range(3)):
                        print(f"✅ Color changed to target after {time.time() - start_time:.2f}s")
                        return True
                time.sleep(0.1)
            
            print(f"❌ Color did not change within {timeout}s")
            return False
        except Exception as e:
            print(f"❌ Wait for color change failed: {str(e)}")
            return False
    
    def get_screen_info(self) -> Dict:
        """Get screen information"""
        return {
            'width': self.screen_width,
            'height': self.screen_height,
            'mouse_position': self.get_mouse_position(),
            'platform': pyautogui.platform
        }
    
    def safe_zone(self, x: int, y: int) -> bool:
        """Check if coordinates are within safe zone (not in corners)"""
        corner_size = 50
        return (corner_size <= x <= self.screen_width - corner_size and 
                corner_size <= y <= self.screen_height - corner_size)

# Usage example
if __name__ == "__main__":
    controller = MouseKeyboardController()
    
    # Get screen info
    info = controller.get_screen_info()
    print(f"Screen info: {info}")
    
    # Example actions
    controller.move_mouse(100, 100)
    controller.click()
    controller.type_text("Hello World!")
    controller.press_key('enter')
    
    # Take screenshot
    controller.take_screenshot(save_path="test_screenshot.png") 