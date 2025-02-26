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
from sklearn.preprocessing import StandardScaler

from solar_forecast.utils import calculate_theoretical_solar_radiation

# Define model directory
MODEL_DIR = os.path.join(settings.BASE_DIR, "solar_forecast", "models")

class HybridSolarPredictor:
    def __init__(self):
        self.cnn_model = None
        self.catboost_model = None
        self.scaler = StandardScaler()
        self.load_models()

    def load_models(self):
        try:
            # Load CNN model
            cnn_path = os.path.join(MODEL_DIR, "solar_model_cnn.keras")
            self.cnn_model = load_model(cnn_path) if os.path.exists(cnn_path) else None

            # Load CatBoost model
            catboost_path = os.path.join(MODEL_DIR, "solar_model_catboost.cbm")
            self.catboost_model = CatBoostRegressor().load_model(catboost_path) if os.path.exists(catboost_path) else None

        except Exception as e:
            print(f"Error loading models: {str(e)}")

    def predict(self, features):
        """
        Make predictions using both models and ensemble the results
        """
        try:
            # Prepare input data
            features_array = np.array(features).reshape(1, -1)
            features_scaled = self.scaler.transform(features_array)
            
            predictions = []
            weights = []

            # CNN prediction
            if self.cnn_model:
                cnn_input = features_scaled.reshape((1, features_scaled.shape[1], 1))
                cnn_pred = self.cnn_model.predict(cnn_input, verbose=0)[0][0]
                predictions.append(cnn_pred)
                weights.append(0.6)  # Weight for CNN

            # CatBoost prediction
            if self.catboost_model:
                catboost_pred = self.catboost_model.predict(features_array)[0]
                predictions.append(catboost_pred)
                weights.append(0.4)  # Weight for CatBoost

            # Ensemble prediction
            if predictions:
                weighted_pred = np.average(predictions, weights=weights)
                return round(weighted_pred, 2)
            else:
                return calculate_theoretical_solar_radiation(*features)

        except Exception as e:
            print(f"Prediction error: {str(e)}")
            return calculate_theoretical_solar_radiation(*features)

def predict_solar_radiation(temp, humidity, wind_speed, precipitation, cloud_coverage):
    """
    Main prediction function using hybrid model
    """
    features = [temp, humidity, wind_speed, precipitation, cloud_coverage]
    predictor = HybridSolarPredictor()
    return predictor.predict(features)

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