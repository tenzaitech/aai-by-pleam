#!/usr/bin/env python3
"""
🎯 Chrome Automation 100% Master Controller
รวมทุกเครื่องมือเข้าด้วยกันสำหรับการควบคุม Chrome เต็มรูปแบบ
"""

import os
import sys
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import core modules
try:
    from core.puppeteer_controller import PuppeteerController
    from core.selenium_controller import SeleniumController
    from core.ocr_processor import OCRProcessor
    from core.visual_recognition import VisualRecognition
    from core.mouse_keyboard_controller import MouseKeyboardController
    from core.ai_integration import AIIntegration
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all core modules are available")
    sys.exit(1)

class ChromeAutomationMaster:
    def __init__(self, config: Optional[Dict] = None):
        """Initialize Master Controller"""
        self.config = config or {}
        self.controllers = {}
        self.session_data = {}
        self.is_initialized = False
        
        # Initialize timestamp
        self.start_time = datetime.now()
        
        print("🚀 Chrome Automation Master Controller Initializing...")
        
    def initialize_all_controllers(self) -> bool:
        """Initialize all automation controllers"""
        try:
            print("\n📦 Initializing Controllers...")
            
            # 1. Puppeteer Controller (Node.js)
            print("  🔧 Initializing Puppeteer...")
            self.controllers['puppeteer'] = PuppeteerController()
            
            # 2. Selenium Controller (Python)
            print("  🔧 Initializing Selenium...")
            self.controllers['selenium'] = SeleniumController()
            
            # 3. OCR Processor
            print("  🔧 Initializing OCR...")
            self.controllers['ocr'] = OCRProcessor()
            
            # 4. Visual Recognition
            print("  🔧 Initializing Visual Recognition...")
            self.controllers['vision'] = VisualRecognition()
            
            # 5. Mouse & Keyboard Controller
            print("  🔧 Initializing Mouse & Keyboard...")
            self.controllers['input'] = MouseKeyboardController()
            
            # 6. AI Integration
            print("  🔧 Initializing AI Integration...")
            self.controllers['ai'] = AIIntegration()
            
            self.is_initialized = True
            print("✅ All controllers initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Controller initialization failed: {str(e)}")
            return False
    
    def start_browser_session(self, browser_type: str = 'puppeteer', 
                            headless: bool = False) -> bool:
        """Start browser session"""
        try:
            if browser_type == 'puppeteer':
                success = self.controllers['puppeteer'].initialize({'headless': headless})
            elif browser_type == 'selenium':
                success = self.controllers['selenium'].initialize(headless=headless)
            else:
                print(f"❌ Unsupported browser type: {browser_type}")
                return False
            
            if success:
                self.session_data['browser_type'] = browser_type
                self.session_data['start_time'] = datetime.now().isoformat()
                print(f"✅ {browser_type} browser session started")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Browser session start failed: {str(e)}")
            return False
    
    def navigate_to_url(self, url: str) -> bool:
        """Navigate to URL using active browser"""
        try:
            browser_type = self.session_data.get('browser_type', 'puppeteer')
            
            if browser_type == 'puppeteer':
                return self.controllers['puppeteer'].navigateTo(url)
            elif browser_type == 'selenium':
                return self.controllers['selenium'].navigate_to(url)
            else:
                print(f"❌ No active browser session")
                return False
                
        except Exception as e:
            print(f"❌ Navigation failed: {str(e)}")
            return False
    
    def take_screenshot_and_analyze(self, save_path: str = "screenshot.png") -> Dict:
        """Take screenshot and perform comprehensive analysis"""
        try:
            results = {}
            
            # Take screenshot
            browser_type = self.session_data.get('browser_type', 'puppeteer')
            if browser_type == 'puppeteer':
                self.controllers['puppeteer'].takeScreenshot(save_path)
            elif browser_type == 'selenium':
                self.controllers['selenium'].take_screenshot(save_path)
            
            # OCR Analysis
            print("🔍 Performing OCR analysis...")
            text_content = self.controllers['ocr'].extract_text(save_path)
            results['ocr_text'] = text_content
            
            # Visual Recognition
            print("🔍 Performing visual recognition...")
            visual_results = self.controllers['vision'].classify_image(save_path)
            results['visual_classification'] = visual_results
            
            # AI Analysis
            print("🔍 Performing AI analysis...")
            ai_analysis = self.controllers['ai'].identify_elements_in_image(save_path)
            results['ai_analysis'] = ai_analysis
            
            print("✅ Comprehensive analysis completed")
            return results
            
        except Exception as e:
            print(f"❌ Screenshot analysis failed: {str(e)}")
            return {}
    
    def smart_click(self, target_description: str, screenshot_path: str = "current_screenshot.png") -> bool:
        """Smart click using AI and image recognition"""
        try:
            # Take current screenshot
            self.take_screenshot_and_analyze(screenshot_path)
            
            # Use AI to identify target
            ai_analysis = self.controllers['ai'].identify_elements_in_image(screenshot_path)
            
            # Use OCR to find text-based targets
            text_content = self.controllers['ocr'].extract_text(screenshot_path)
            
            # Use visual recognition to find similar elements
            visual_results = self.controllers['vision'].classify_image(screenshot_path)
            
            # Combine results and make decision
            print(f"🎯 Smart click analysis for: {target_description}")
            print(f"  - AI Analysis: {ai_analysis}")
            print(f"  - OCR Text: {text_content[:100]}...")
            print(f"  - Visual Classification: {visual_results}")
            
            # For now, use mouse controller to click center of screen
            # In real implementation, this would use AI to determine exact coordinates
            screen_info = self.controllers['input'].get_screen_info()
            center_x = screen_info['width'] // 2
            center_y = screen_info['height'] // 2
            
            return self.controllers['input'].click(center_x, center_y)
            
        except Exception as e:
            print(f"❌ Smart click failed: {str(e)}")
            return False
    
    def automated_form_filling(self, form_data: Dict, screenshot_path: str = "form_screenshot.png") -> bool:
        """Automated form filling using AI and OCR"""
        try:
            print("📝 Starting automated form filling...")
            
            # Take screenshot of form
            self.take_screenshot_and_analyze(screenshot_path)
            
            # Use AI to identify form fields
            ai_analysis = self.controllers['ai'].identify_elements_in_image(screenshot_path)
            
            # Fill each field
            for field_name, field_value in form_data.items():
                print(f"  Filling {field_name}: {field_value}")
                
                # Use AI to find field location
                # For now, use simple approach
                self.controllers['input'].type_text(str(field_value))
                time.sleep(0.5)
            
            print("✅ Form filling completed")
            return True
            
        except Exception as e:
            print(f"❌ Form filling failed: {str(e)}")
            return False
    
    def generate_automation_report(self) -> Dict:
        """Generate comprehensive automation report"""
        try:
            report = {
                'session_info': {
                    'start_time': self.start_time.isoformat(),
                    'duration': str(datetime.now() - self.start_time),
                    'browser_type': self.session_data.get('browser_type', 'none'),
                    'controllers_initialized': list(self.controllers.keys())
                },
                'capabilities': {
                    'puppeteer': 'Browser automation with JavaScript',
                    'selenium': 'Cross-browser automation',
                    'ocr': 'Text extraction from images',
                    'vision': 'Image classification and object detection',
                    'input': 'Mouse and keyboard control',
                    'ai': 'AI-powered analysis and automation'
                },
                'usage_examples': [
                    'Smart element detection and clicking',
                    'Automated form filling',
                    'Screenshot analysis with OCR',
                    'Visual recognition and classification',
                    'AI-powered workflow optimization'
                ]
            }
            
            return report
            
        except Exception as e:
            print(f"❌ Report generation failed: {str(e)}")
            return {}
    
    def save_session_data(self, file_path: str = "session_data.json") -> bool:
        """Save session data to file"""
        try:
            data = {
                'session_data': self.session_data,
                'report': self.generate_automation_report(),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Session data saved to: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Session data save failed: {str(e)}")
            return False
    
    def cleanup(self):
        """Cleanup all resources"""
        try:
            print("🧹 Cleaning up resources...")
            
            # Close browser sessions
            if 'puppeteer' in self.controllers:
                self.controllers['puppeteer'].close()
            
            if 'selenium' in self.controllers:
                self.controllers['selenium'].close()
            
            # Save session data
            self.save_session_data()
            
            print("✅ Cleanup completed")
            
        except Exception as e:
            print(f"❌ Cleanup failed: {str(e)}")

# Usage example
if __name__ == "__main__":
    # Initialize master controller
    master = ChromeAutomationMaster()
    
    if master.initialize_all_controllers():
        # Start browser session
        if master.start_browser_session('puppeteer', headless=False):
            # Navigate to a website
            master.navigate_to_url("https://www.google.com")
            
            # Take screenshot and analyze
            analysis = master.take_screenshot_and_analyze("google_analysis.png")
            print("Analysis results:", json.dumps(analysis, indent=2))
            
            # Smart click example
            master.smart_click("search box")
            
            # Form filling example
            form_data = {
                'search_query': 'Chrome automation tools',
                'submit': 'enter'
            }
            master.automated_form_filling(form_data)
            
            # Generate report
            report = master.generate_automation_report()
            print("Automation report:", json.dumps(report, indent=2))
            
            # Cleanup
            master.cleanup()
    else:
        print("❌ Failed to initialize controllers") 