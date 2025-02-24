from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
from pathlib import Path
import shutil
import io
from PIL import Image

app = FastAPI(title="Plant Disease Detection API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the model (adjust path as needed)
MODEL_PATH = Path("pdd/models/plant_disease_model.h5")
model = tf.keras.models.load_model(MODEL_PATH)

# Define class names (adjust based on your model's classes)
CLASS_NAMES = ['Healthy', 'Bacterial Leaf Blight', 'Leaf Spot', 'Powdery Mildew']

def preprocess_image(image: Image.Image) -> np.ndarray:
    """Preprocess the image for model prediction."""
    img = image.resize((224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)
    return tf.keras.applications.mobilenet_v2.preprocess_input(img_array)

@app.get("/")
async def root():
    return {"message": "Plant Disease Detection API"}

@app.post("/predict/")
async def predict_disease(file: UploadFile = File(...)):
    try:
        # Read and validate image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Preprocess image
        processed_image = preprocess_image(image)
        
        # Make prediction
        predictions = model.predict(processed_image)
        predicted_class = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class])
        
        return {
            "filename": file.filename,
            "disease": CLASS_NAMES[predicted_class],
            "confidence": confidence,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 