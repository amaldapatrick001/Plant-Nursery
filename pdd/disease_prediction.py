import cv2
import numpy as np
from pathlib import Path
from .models import Disease, Treatment

def preprocess_image(image_path):
    """Preprocess the image for prediction"""
    try:
        # Read and resize image to 100x100 (matching your dataset size)
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError("Unable to read image")
        
        img = cv2.resize(img, (100, 100))  # Resize to match your dataset
        img = img / 255.0  # Normalize pixel values
        return img
    
    except Exception as e:
        raise Exception(f"Error preprocessing image: {str(e)}")

def predict_disease_from_image(image_path):
    """Main function to predict plant disease"""
    try:
        # Preprocess the image
        processed_image = preprocess_image(image_path)
        
        # Your model prediction code here
        # This should return a label_id and confidence score
        prediction = get_model_prediction(processed_image)
        
        # Get disease from database
        try:
            disease = Disease.objects.get(label_id=prediction['label_id'])
            treatments = disease.treatments.all()
            
            treatment_list = []
            for treatment in treatments:
                treatment_list.extend([
                    treatment.description,
                    treatment.prevention_measures
                ])
            
            return {
                'success': True,
                'disease_name': disease.name,
                'confidence': prediction['confidence'] * 100,
                'description': disease.description,
                'symptoms': disease.symptoms,
                'treatments': treatment_list
            }
        except Disease.DoesNotExist:
            raise Exception("Disease not found in database")
            
    except Exception as e:
        return {
            'success': False,
            'disease_name': 'Unknown',
            'confidence': 0.0,
            'error': str(e),
            'treatments': ['Error in disease detection. Please try again.']
        }

def get_model_prediction(processed_image):
    """
    Placeholder for your model prediction code
    Replace this with your actual model implementation
    """
    # This is where you'll implement your actual model prediction
    # For now, returning dummy data
    return {
        'label_id': 0,
        'confidence': 0.95
    }

def get_treatment_recommendations(disease_name):
    """Get treatment recommendations based on disease"""
    # Add basic treatment recommendations
    treatments = {
        'Apple Scab Leaf': [
            'Remove infected leaves and fruit',
            'Apply fungicide during growing season',
            'Maintain good air circulation by proper pruning'
        ],
        'Tomato leaf bacterial spot': [
            'Remove infected plants',
            'Avoid overhead watering',
            'Use copper-based fungicides'
        ],
        # Add more diseases and their treatments here
    }
    
    return treatments.get(disease_name, ['Please consult a plant pathologist for specific treatment recommendations.'])

# Test function
def test_prediction():
    """Test the prediction system"""
    test_image_path = "path/to/test/image.jpg"  # Replace with actual test image path
    result = predict_disease_from_image(test_image_path)
    print("Prediction Result:", result) 