import cv2
import numpy as np
import pytesseract
from PIL import Image
import os
from typing import List, Dict, Tuple

class OCRProcessor:
    def __init__(self, tesseract_path=None):
        """Initialize OCR Processor"""
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        self.supported_languages = ['eng', 'tha', 'chi_sim', 'jpn', 'kor']
        
    def preprocess_image(self, image_path: str, enhance_text: bool = True) -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            # Read image
            if isinstance(image_path, str):
                image = cv2.imread(image_path)
            else:
                image = image_path.copy()
            
            if image is None:
                raise ValueError("Could not read image")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            if enhance_text:
                # Apply noise reduction
                denoised = cv2.fastNlMeansDenoising(gray)
                
                # Apply adaptive thresholding
                thresh = cv2.adaptiveThreshold(
                    denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY, 11, 2
                )
                
                # Apply morphological operations
                kernel = np.ones((1, 1), np.uint8)
                processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                
                return processed
            else:
                return gray
                
        except Exception as e:
            print(f"❌ Image preprocessing failed: {str(e)}")
            return None
    
    def extract_text(self, image_path: str, languages: List[str] = ['eng'], 
                    config: str = '--psm 6') -> str:
        """Extract text from image"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            if processed_image is None:
                return ""
            
            # Prepare language string
            lang_string = '+'.join(languages)
            
            # Extract text
            text = pytesseract.image_to_string(
                processed_image, 
                lang=lang_string, 
                config=config
            )
            
            # Clean text
            text = self.clean_text(text)
            
            print(f"✅ Text extracted successfully")
            return text
            
        except Exception as e:
            print(f"❌ Text extraction failed: {str(e)}")
            return ""
    
    def extract_text_with_boxes(self, image_path: str, languages: List[str] = ['eng']) -> List[Dict]:
        """Extract text with bounding boxes"""
        try:
            processed_image = self.preprocess_image(image_path)
            if processed_image is None:
                return []
            
            lang_string = '+'.join(languages)
            
            # Get data with bounding boxes
            data = pytesseract.image_to_data(
                processed_image, 
                lang=lang_string, 
                output_type=pytesseract.Output.DICT
            )
            
            # Process results
            results = []
            for i in range(len(data['text'])):
                if data['conf'][i] > 30:  # Confidence threshold
                    result = {
                        'text': data['text'][i],
                        'confidence': data['conf'][i],
                        'bbox': {
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        }
                    }
                    results.append(result)
            
            print(f"✅ Extracted {len(results)} text elements with boxes")
            return results
            
        except Exception as e:
            print(f"❌ Text extraction with boxes failed: {str(e)}")
            return []
    
    def find_text_in_image(self, image_path: str, search_text: str, 
                          languages: List[str] = ['eng']) -> List[Dict]:
        """Find specific text in image"""
        try:
            results = self.extract_text_with_boxes(image_path, languages)
            
            found_results = []
            search_text_lower = search_text.lower()
            
            for result in results:
                if search_text_lower in result['text'].lower():
                    found_results.append(result)
            
            print(f"✅ Found {len(found_results)} matches for '{search_text}'")
            return found_results
            
        except Exception as e:
            print(f"❌ Text search failed: {str(e)}")
            return []
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters (keep letters, numbers, spaces)
        import re
        text = re.sub(r'[^\w\s]', '', text)
        
        return text.strip()
    
    def get_text_confidence(self, image_path: str, languages: List[str] = ['eng']) -> float:
        """Get average confidence of OCR results"""
        try:
            results = self.extract_text_with_boxes(image_path, languages)
            
            if not results:
                return 0.0
            
            confidences = [result['confidence'] for result in results]
            avg_confidence = sum(confidences) / len(confidences)
            
            return avg_confidence
            
        except Exception as e:
            print(f"❌ Confidence calculation failed: {str(e)}")
            return 0.0
    
    def save_processed_image(self, image_path: str, output_path: str) -> bool:
        """Save preprocessed image"""
        try:
            processed_image = self.preprocess_image(image_path)
            if processed_image is not None:
                cv2.imwrite(output_path, processed_image)
                print(f"✅ Processed image saved: {output_path}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Save processed image failed: {str(e)}")
            return False

# Usage example
if __name__ == "__main__":
    ocr = OCRProcessor()
    
    # Example usage
    image_path = "screenshot.png"
    if os.path.exists(image_path):
        # Extract text
        text = ocr.extract_text(image_path, ['eng', 'tha'])
        print(f"Extracted text: {text}")
        
        # Find specific text
        results = ocr.find_text_in_image(image_path, "search")
        print(f"Found results: {results}")
        
        # Get confidence
        confidence = ocr.get_text_confidence(image_path)
        print(f"Average confidence: {confidence:.2f}%") 