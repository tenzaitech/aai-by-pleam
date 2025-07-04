import openai
import requests
import json
import base64
import os
from typing import List, Dict, Optional, Any
from PIL import Image
import io

class AIIntegration:
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize AI Integration"""
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        self.vision_model = "gpt-4-vision-preview"
        self.text_model = "gpt-4"
        
        print("✅ AI Integration initialized")
    
    def analyze_image_with_vision(self, image_path: str, prompt: str) -> Optional[Dict]:
        """Analyze image using OpenAI Vision API"""
        try:
            if not self.openai_api_key:
                print("❌ OpenAI API key not found")
                return None
            
            # Encode image
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prepare message
            message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        }
                    }
                ]
            }
            
            # Make API call
            response = openai.ChatCompletion.create(
                model=self.vision_model,
                messages=[message],
                max_tokens=1000
            )
            
            result = {
                'analysis': response.choices[0].message.content,
                'model': self.vision_model,
                'tokens_used': response.usage.total_tokens
            }
            
            print("✅ Image analysis completed")
            return result
            
        except Exception as e:
            print(f"❌ Image analysis failed: {str(e)}")
            return None
    
    def extract_text_from_image(self, image_path: str) -> Optional[str]:
        """Extract text from image using Vision API"""
        prompt = """
        Please extract all text from this image. 
        Return only the text content, no explanations.
        If there are multiple languages, preserve them as they appear.
        """
        
        result = self.analyze_image_with_vision(image_path, prompt)
        if result:
            return result['analysis']
        return None
    
    def identify_elements_in_image(self, image_path: str) -> Optional[Dict]:
        """Identify UI elements in image"""
        prompt = """
        Analyze this screenshot and identify all UI elements:
        - Buttons, links, input fields
        - Text content and labels
        - Images and icons
        - Layout structure
        
        Return as JSON with element types and their descriptions.
        """
        
        result = self.analyze_image_with_vision(image_path, prompt)
        if result:
            try:
                # Try to parse as JSON
                return json.loads(result['analysis'])
            except:
                # Return as text if not valid JSON
                return {'elements': result['analysis']}
        return None
    
    def generate_automation_script(self, image_path: str, task_description: str) -> Optional[str]:
        """Generate automation script based on image and task"""
        prompt = f"""
        Based on this screenshot and the task description: "{task_description}"
        
        Generate a Python automation script using:
        - pyautogui for mouse/keyboard control
        - Image recognition for finding elements
        - Error handling and safety measures
        
        The script should be complete and ready to run.
        """
        
        result = self.analyze_image_with_vision(image_path, prompt)
        if result:
            return result['analysis']
        return None
    
    def analyze_webpage_structure(self, html_content: str) -> Optional[Dict]:
        """Analyze webpage structure using AI"""
        try:
            if not self.openai_api_key:
                return None
            
            prompt = f"""
            Analyze this HTML content and provide:
            1. Main sections and their purposes
            2. Interactive elements (buttons, forms, links)
            3. Data structures and content types
            4. Navigation patterns
            5. Potential automation targets
            
            HTML Content:
            {html_content[:4000]}  # Limit content length
            """
            
            response = openai.ChatCompletion.create(
                model=self.text_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            
            result = {
                'analysis': response.choices[0].message.content,
                'model': self.text_model,
                'tokens_used': response.usage.total_tokens
            }
            
            print("✅ Webpage structure analysis completed")
            return result
            
        except Exception as e:
            print(f"❌ Webpage analysis failed: {str(e)}")
            return None
    
    def generate_selenium_selectors(self, html_content: str, element_description: str) -> Optional[List[str]]:
        """Generate Selenium selectors for elements"""
        try:
            if not self.openai_api_key:
                return None
            
            prompt = f"""
            Given this HTML content and element description: "{element_description}"
            
            Generate multiple Selenium selectors (CSS, XPath, ID, class) to locate this element.
            Return as a JSON array of selector strings.
            
            HTML Content:
            {html_content[:3000]}
            """
            
            response = openai.ChatCompletion.create(
                model=self.text_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            try:
                selectors = json.loads(response.choices[0].message.content)
                print(f"✅ Generated {len(selectors)} selectors")
                return selectors
            except:
                # Return as text if not valid JSON
                return [response.choices[0].message.content]
                
        except Exception as e:
            print(f"❌ Selector generation failed: {str(e)}")
            return None
    
    def optimize_automation_workflow(self, workflow_description: str, 
                                   current_issues: List[str]) -> Optional[str]:
        """Optimize automation workflow using AI"""
        try:
            if not self.openai_api_key:
                return None
            
            issues_text = "\n".join([f"- {issue}" for issue in current_issues])
            
            prompt = f"""
            Current automation workflow: {workflow_description}
            
            Current issues:
            {issues_text}
            
            Please provide:
            1. Analysis of the issues
            2. Optimized workflow steps
            3. Code improvements
            4. Best practices recommendations
            5. Error handling strategies
            """
            
            response = openai.ChatCompletion.create(
                model=self.text_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            
            print("✅ Workflow optimization completed")
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Workflow optimization failed: {str(e)}")
            return None
    
    def create_test_scenarios(self, application_description: str, 
                            test_type: str = "automation") -> Optional[List[Dict]]:
        """Create test scenarios using AI"""
        try:
            if not self.openai_api_key:
                return None
            
            prompt = f"""
            Create comprehensive {test_type} test scenarios for: {application_description}
            
            For each scenario provide:
            - Test name and description
            - Preconditions
            - Test steps
            - Expected results
            - Automation approach
            
            Return as JSON array of test objects.
            """
            
            response = openai.ChatCompletion.create(
                model=self.text_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            
            try:
                scenarios = json.loads(response.choices[0].message.content)
                print(f"✅ Created {len(scenarios)} test scenarios")
                return scenarios
            except:
                return [{'scenario': response.choices[0].message.content}]
                
        except Exception as e:
            print(f"❌ Test scenario creation failed: {str(e)}")
            return None
    
    def analyze_error_logs(self, error_logs: str) -> Optional[Dict]:
        """Analyze error logs and provide solutions"""
        try:
            if not self.openai_api_key:
                return None
            
            prompt = f"""
            Analyze these automation error logs and provide:
            1. Error classification and severity
            2. Root cause analysis
            3. Recommended solutions
            4. Prevention strategies
            5. Code fixes if applicable
            
            Error Logs:
            {error_logs[:3000]}
            """
            
            response = openai.ChatCompletion.create(
                model=self.text_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            
            result = {
                'analysis': response.choices[0].message.content,
                'model': self.text_model,
                'tokens_used': response.usage.total_tokens
            }
            
            print("✅ Error log analysis completed")
            return result
            
        except Exception as e:
            print(f"❌ Error log analysis failed: {str(e)}")
            return None

# Usage example
if __name__ == "__main__":
    ai = AIIntegration()
    
    # Example usage
    image_path = "screenshot.png"
    if os.path.exists(image_path):
        # Extract text
        text = ai.extract_text_from_image(image_path)
        print(f"Extracted text: {text}")
        
        # Identify elements
        elements = ai.identify_elements_in_image(image_path)
        print(f"Identified elements: {elements}")
        
        # Generate automation script
        script = ai.generate_automation_script(image_path, "Click the login button")
        print(f"Generated script: {script}") 