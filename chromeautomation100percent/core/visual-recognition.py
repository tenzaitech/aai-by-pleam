import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications import VGG16, ResNet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import preprocess_input, decode_predictions
import matplotlib.pyplot as plt
import os
from typing import List, Dict, Tuple, Optional

class VisualRecognition:
    def __init__(self, model_type: str = 'vgg16'):
        """Initialize Visual Recognition with pre-trained model"""
        self.model_type = model_type
        self.model = None
        self.load_model()
        
    def load_model(self):
        """Load pre-trained model"""
        try:
            if self.model_type == 'vgg16':
                self.model = VGG16(weights='imagenet', include_top=True)
            elif self.model_type == 'resnet50':
                self.model = ResNet50(weights='imagenet', include_top=True)
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
                
            print(f"✅ {self.model_type.upper()} model loaded successfully")
            
        except Exception as e:
            print(f"❌ Model loading failed: {str(e)}")
            self.model = None
    
    def preprocess_image_for_model(self, image_path: str, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
        """Preprocess image for model input"""
        try:
            # Load and resize image
            img = image.load_img(image_path, target_size=target_size)
            
            # Convert to array
            x = image.img_to_array(img)
            
            # Add batch dimension
            x = np.expand_dims(x, axis=0)
            
            # Preprocess for VGG16/ResNet
            x = preprocess_input(x)
            
            return x
            
        except Exception as e:
            print(f"❌ Image preprocessing failed: {str(e)}")
            return None
    
    def classify_image(self, image_path: str, top_k: int = 5) -> List[Dict]:
        """Classify image using pre-trained model"""
        try:
            if self.model is None:
                raise ValueError("Model not loaded")
            
            # Preprocess image
            x = self.preprocess_image_for_model(image_path)
            if x is None:
                return []
            
            # Predict
            predictions = self.model.predict(x)
            
            # Decode predictions
            decoded = decode_predictions(predictions, top=top_k)[0]
            
            # Format results
            results = []
            for class_id, class_name, confidence in decoded:
                results.append({
                    'class_id': class_id,
                    'class_name': class_name,
                    'confidence': float(confidence) * 100
                })
            
            print(f"✅ Image classified successfully")
            return results
            
        except Exception as e:
            print(f"❌ Image classification failed: {str(e)}")
            return []
    
    def detect_objects(self, image_path: str, confidence_threshold: float = 0.5) -> List[Dict]:
        """Detect objects in image using OpenCV"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not read image")
            
            # Convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Load pre-trained object detection model
            net = cv2.dnn.readNetFromCaffe(
                'models/deploy.prototxt',
                'models/mobilenet_ssd.caffemodel'
            )
            
            # Prepare image for detection
            blob = cv2.dnn.blobFromImage(
                cv2.resize(image, (300, 300)), 
                0.007843, (300, 300), 127.5
            )
            
            # Detect objects
            net.setInput(blob)
            detections = net.forward()
            
            # Process results
            objects = []
            height, width = image.shape[:2]
            
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                
                if confidence > confidence_threshold:
                    class_id = int(detections[0, 0, i, 1])
                    
                    # Get bounding box
                    box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                    x1, y1, x2, y2 = box.astype(int)
                    
                    objects.append({
                        'class_id': class_id,
                        'confidence': float(confidence) * 100,
                        'bbox': {
                            'x1': x1, 'y1': y1,
                            'x2': x2, 'y2': y2,
                            'width': x2 - x1,
                            'height': y2 - y1
                        }
                    })
            
            print(f"✅ Detected {len(objects)} objects")
            return objects
            
        except Exception as e:
            print(f"❌ Object detection failed: {str(e)}")
            return []
    
    def find_similar_images(self, reference_image: str, target_folder: str, 
                          similarity_threshold: float = 0.8) -> List[Dict]:
        """Find similar images in a folder"""
        try:
            # Load reference image features
            ref_features = self.extract_features(reference_image)
            if ref_features is None:
                return []
            
            similar_images = []
            
            # Check each image in target folder
            for filename in os.listdir(target_folder):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    target_path = os.path.join(target_folder, filename)
                    
                    # Extract features
                    target_features = self.extract_features(target_path)
                    if target_features is not None:
                        # Calculate similarity
                        similarity = self.calculate_similarity(ref_features, target_features)
                        
                        if similarity >= similarity_threshold:
                            similar_images.append({
                                'path': target_path,
                                'filename': filename,
                                'similarity': similarity
                            })
            
            # Sort by similarity
            similar_images.sort(key=lambda x: x['similarity'], reverse=True)
            
            print(f"✅ Found {len(similar_images)} similar images")
            return similar_images
            
        except Exception as e:
            print(f"❌ Similar image search failed: {str(e)}")
            return []
    
    def extract_features(self, image_path: str) -> Optional[np.ndarray]:
        """Extract features from image"""
        try:
            if self.model is None:
                return None
            
            # Preprocess image
            x = self.preprocess_image_for_model(image_path)
            if x is None:
                return None
            
            # Extract features (remove classification layer)
            features = self.model.predict(x)
            
            return features.flatten()
            
        except Exception as e:
            print(f"❌ Feature extraction failed: {str(e)}")
            return None
    
    def calculate_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Calculate cosine similarity between feature vectors"""
        try:
            # Normalize vectors
            norm1 = np.linalg.norm(features1)
            norm2 = np.linalg.norm(features2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(features1, features2) / (norm1 * norm2)
            
            return float(similarity)
            
        except Exception as e:
            print(f"❌ Similarity calculation failed: {str(e)}")
            return 0.0
    
    def save_analysis_result(self, image_path: str, results: List[Dict], 
                           output_path: str) -> bool:
        """Save analysis results with visualization"""
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                return False
            
            # Create visualization
            plt.figure(figsize=(12, 8))
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            
            # Add text annotations
            y_offset = 30
            for i, result in enumerate(results[:5]):  # Top 5 results
                if 'class_name' in result:
                    text = f"{result['class_name']}: {result['confidence']:.2f}%"
                    plt.text(10, y_offset + i * 25, text, 
                            fontsize=12, color='white', 
                            bbox=dict(boxstyle="round,pad=0.3", facecolor="red"))
            
            plt.title("Visual Recognition Results")
            plt.axis('off')
            plt.tight_layout()
            
            # Save result
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Analysis result saved: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Save analysis result failed: {str(e)}")
            return False

# Usage example
if __name__ == "__main__":
    vr = VisualRecognition('vgg16')
    
    # Example usage
    image_path = "test_image.jpg"
    if os.path.exists(image_path):
        # Classify image
        results = vr.classify_image(image_path)
        print("Classification results:")
        for result in results:
            print(f"- {result['class_name']}: {result['confidence']:.2f}%")
        
        # Save analysis
        vr.save_analysis_result(image_path, results, "analysis_result.png") 