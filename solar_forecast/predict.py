import os
import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
from catboost import CatBoostRegressor
from tensorflow.keras.models import load_model
from django.conf import settings
from datetime import datetime, timedelta
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense

from solar_forecast.utils import calculate_theoretical_solar_radiation

# Define model directory
MODEL_DIR = os.path.join(settings.BASE_DIR, "solar_forecast", "models")

def predict_solar_radiation(temp, humidity, wind_speed, precipitation, cloud_coverage):
    """
    Predicts solar radiation using trained model with fallback to theoretical calculation
    
    Args:
        temp (float): Temperature in Celsius
        humidity (float): Relative humidity percentage
        wind_speed (float): Wind speed in m/s
        precipitation (float): Precipitation in mm
        cloud_coverage (float): Cloud coverage percentage
    
    Returns:
        float: Predicted solar radiation in W/m²
    """
    try:
        # Prepare input data
        features = np.array([temp, humidity, wind_speed, precipitation, cloud_coverage])
        input_data = features.reshape((1, 5, 1))  # (batch_size, features, channels)
        
        # Load model
        model_path = os.path.join(MODEL_DIR, "solar_model.keras")
        if not os.path.exists(model_path):
            print("Model file not found, using theoretical calculation")
            return calculate_theoretical_solar_radiation(temp, humidity, wind_speed, precipitation, cloud_coverage)
            
        model = load_model(model_path)
        
        # Make prediction
        prediction = model.predict(input_data, verbose=0)
        predicted_value = float(prediction[0][0])
        
        # Validate prediction with more strict bounds
        today_radiation = 230.1  # Current day's radiation
        max_deviation = 0.5  # Maximum 50% deviation from current day
        min_value = today_radiation * (1 - max_deviation)
        max_value = today_radiation * (1 + max_deviation)
        
        if predicted_value < min_value or predicted_value > max_value:
            print(f"Prediction {predicted_value:.2f} W/m² outside reasonable range [{min_value:.2f}, {max_value:.2f}]")
            theoretical_value = calculate_theoretical_solar_radiation(
                temp, humidity, wind_speed, precipitation, cloud_coverage
            )
            # Average with theoretical calculation for more stability
            return round((theoretical_value + today_radiation * 0.8) / 2, 2)
            
        return round(predicted_value, 2)
        
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        return calculate_theoretical_solar_radiation(temp, humidity, wind_speed, precipitation, cloud_coverage)

def create_model():
    """Creates the CNN model architecture"""
    model = tf.keras.Sequential([
        tf.keras.layers.Conv1D(32, 3, activation='relu', input_shape=(5, 1)),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    return model

def prepare_data(X, y):
    """Prepares data for CNN model"""
    X = X.reshape((X.shape[0], X.shape[1], 1))
    return X, y