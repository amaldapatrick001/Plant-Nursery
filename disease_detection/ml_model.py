import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np

# Define the model path
MODEL_PATH = 'plant_disease_model.h5'

# Simplified plant species and diseases dictionary
PLANT_SPECIES = {
    'tomato': ['Early Blight', 'Late Blight', 'Healthy'],
    'potato': ['Early Blight', 'Late Blight', 'Healthy'],
    'pepper': ['Bacterial Spot', 'Healthy'],
    'apple': ['Apple Scab', 'Black Rot', 'Healthy']
}

# Treatment suggestions database
TREATMENT_SUGGESTIONS = {
    'Early Blight': [
        "Remove infected leaves immediately",
        "Apply copper-based fungicide",
        "Ensure proper plant spacing",
        "Water at the base of plants"
    ],
    'Late Blight': [
        "Remove and destroy infected plants",
        "Apply fungicide preventatively",
        "Improve drainage",
        "Avoid overhead watering"
    ],
    'Bacterial Spot': [
        "Remove infected plant parts",
        "Apply copper-based bactericide",
        "Rotate crops annually",
        "Avoid working with wet plants"
    ],
    'Healthy': [
        "Continue regular maintenance",
        "Monitor for early signs of disease",
        "Follow proper watering schedule",
        "Maintain good garden hygiene"
    ]
}

def load_model():
    """Load the trained model."""
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        return model
    except:
        # Fallback to a basic MobileNetV2 model
        base_model = MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        x = base_model.output
        x = tf.keras.layers.GlobalAveragePooling2D()(x)
        x = tf.keras.layers.Dense(128, activation='relu')(x)
        predictions = tf.keras.layers.Dense(
            len(PLANT_SPECIES), 
            activation='softmax'
        )(x)
        model = tf.keras.Model(inputs=base_model.input, outputs=predictions)
        return model

def prepare_image(img_path):
    """Preprocess the image for model prediction."""
    try:
        img = load_img(img_path, target_size=(224, 224))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        return img_array
    except Exception as e:
        print(f"Error preprocessing image: {str(e)}")
        return None

def identify_plant_and_disease(img_path):
    """Identifies plant species and checks for diseases."""
    try:
        # Load the model
        model = load_model()
        
        # Prepare the image
        img_array = prepare_image(img_path)
        if img_array is None:
            raise ValueError("Failed to process image")

        # Get predictions
        predictions = model.predict(img_array)
        
        # Identify plant
        plant_index = np.argmax(predictions[0]) % len(PLANT_SPECIES)
        plant_name = list(PLANT_SPECIES.keys())[plant_index]
        plant_confidence = float(np.max(predictions[0]) * 100)
        
        # Identify disease
        possible_diseases = PLANT_SPECIES[plant_name]
        disease_index = np.argmax(predictions[0]) % len(possible_diseases)
        disease_name = possible_diseases[disease_index]
        disease_confidence = float(np.max(predictions[0]) * 100)
        
        # Get treatment suggestions
        treatments = TREATMENT_SUGGESTIONS.get(disease_name, [])
        
        return {
            'plant_name': plant_name,
            'plant_confidence': plant_confidence,
            'disease_name': disease_name,
            'disease_confidence': disease_confidence,
            'treatment_suggestions': treatments
        }
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        return {
            'plant_name': 'Unknown',
            'plant_confidence': 0.0,
            'disease_name': 'Unknown',
            'disease_confidence': 0.0,
            'treatment_suggestions': []
        }