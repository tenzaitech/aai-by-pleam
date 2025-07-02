from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os

class SeleniumController:
    def __init__(self):
        self.driver = None
        self.is_connected = False
        
    def initialize(self, headless=False, chrome_path=None):
        """Initialize Chrome WebDriver"""
        try:
            chrome_options = Options()
            
            if headless:
                chrome_options.add_argument("--headless")
            
            # Performance optimizations
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            
            # Set window size
            chrome_options.add_argument("--window-size=1920,1080")
            
            # User agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            if chrome_path:
                chrome_options.binary_location = chrome_path
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.is_connected = True
            
            print("✅ Selenium initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Selenium initialization failed: {str(e)}")
            return False
    
    def navigate_to(self, url):
        """Navigate to a URL"""
        if not self.is_connected:
            raise Exception("Driver not initialized")
        
        try:
            self.driver.get(url)
            print(f"✅ Navigated to: {url}")
            return True
        except Exception as e:
            print(f"❌ Navigation failed: {str(e)}")
            return False
    
    def find_element(self, by, value, timeout=10):
        """Find element with wait"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            print(f"❌ Element not found: {str(e)}")
            return None
    
    def click_element(self, by, value, timeout=10):
        """Click on element"""
        try:
            element = self.find_element(by, value, timeout)
            if element:
                element.click()
                print(f"✅ Clicked element: {value}")
                return True
            return False
        except Exception as e:
            print(f"❌ Click failed: {str(e)}")
            return False
    
    def type_text(self, by, value, text, timeout=10):
        """Type text in element"""
        try:
            element = self.find_element(by, value, timeout)
            if element:
                element.clear()
                element.send_keys(text)
                print(f"✅ Typed text in: {value}")
                return True
            return False
        except Exception as e:
            print(f"❌ Type failed: {str(e)}")
            return False
    
    def take_screenshot(self, path):
        """Take screenshot"""
        try:
            self.driver.save_screenshot(path)
            print(f"✅ Screenshot saved: {path}")
            return True
        except Exception as e:
            print(f"❌ Screenshot failed: {str(e)}")
            return False
    
    def get_page_source(self):
        """Get page source"""
        try:
            return self.driver.page_source
        except Exception as e:
            print(f"❌ Get page source failed: {str(e)}")
            return None
    
    def execute_script(self, script):
        """Execute JavaScript"""
        try:
            result = self.driver.execute_script(script)
            return result
        except Exception as e:
            print(f"❌ JavaScript execution failed: {str(e)}")
            return None
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for element to be present"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except Exception as e:
            print(f"❌ Wait for element failed: {str(e)}")
            return False
    
    def get_element_text(self, by, value, timeout=10):
        """Get element text"""
        try:
            element = self.find_element(by, value, timeout)
            if element:
                return element.text
            return None
        except Exception as e:
            print(f"❌ Get element text failed: {str(e)}")
            return None
    
    def scroll_to_element(self, by, value, timeout=10):
        """Scroll to element"""
        try:
            element = self.find_element(by, value, timeout)
            if element:
                self.driver.execute_script("arguments[0].scrollIntoView();", element)
                print(f"✅ Scrolled to element: {value}")
                return True
            return False
        except Exception as e:
            print(f"❌ Scroll failed: {str(e)}")
            return False
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            self.is_connected = False
            print("✅ Browser closed")

# Usage example
if __name__ == "__main__":
    controller = SeleniumController()
    if controller.initialize():
        controller.navigate_to("https://www.google.com")
        controller.type_text(By.NAME, "q", "Selenium automation")
        controller.click_element(By.NAME, "btnK")
        time.sleep(3)
        controller.take_screenshot("google_search.png")
        controller.close() 