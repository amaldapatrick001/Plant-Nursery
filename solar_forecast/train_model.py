# solar_forecast/train_model.py

import os
import glob
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import matplotlib.pyplot as plt
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from tensorflow.keras.layers import Input

def load_and_preprocess_data():
    """
    Load and preprocess solar data from all location files
    
    Returns:
        tuple: (X, y) preprocessed features and target variables
    """
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    all_data = []
    
    # Load data from all location files
    for file in glob.glob(os.path.join(data_dir, '*_solar_data.csv')):
        df = pd.read_csv(file, dtype={'timestamp': str})
        all_data.append(df)
    
    # Combine all data
    combined_data = pd.concat(all_data, ignore_index=True)
    
    # Required features - keep synchronized with predict.py
    required_features = [
        'temperature', 
        'humidity', 
        'wind_speed', 
        'precipitation', 
        'cloud_coverage'
    ]
    
    # Verify all required features exist
    for feature in required_features:
        if feature not in combined_data.columns:
            raise ValueError(f"Missing required feature: {feature}")
    
    # Extract hour for filtering
    combined_data['hour'] = pd.to_datetime(combined_data['timestamp'], format='%Y%m%d%H').dt.hour
    
    # Filter for daytime hours (6 AM to 6 PM)
    daytime_mask = (combined_data['hour'] >= 6) & (combined_data['hour'] <= 18)
    combined_data = combined_data[daytime_mask]
    
    # Clean and prepare data
    combined_data = combined_data.dropna()  # Remove any rows with missing values
    
    # Normalize solar radiation values to be between 0 and 1200 W/m²
    combined_data['solar_radiation'] = combined_data['solar_radiation'].clip(0, 1200)
    
    # Extract features and target
    X = combined_data[required_features].values
    y = combined_data['solar_radiation'].values
    
    return X, y

def build_model(input_shape):
    """
    Build the CNN model architecture with improved stability
    """
    model = tf.keras.Sequential([
        tf.keras.layers.Conv1D(32, 3, activation='relu', input_shape=input_shape),
        tf.keras.layers.BatchNormalization(),  # Add normalization
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Dropout(0.2),  # Add dropout
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dense(1)
    ])
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='huber',  # Use Huber loss for better stability
        metrics=['mae']
    )
    return model

def train_catboost_model(X_train, X_test, y_train, y_test):
    """Train CatBoost model"""
    catboost_model = CatBoostRegressor(
        iterations=1000,
        learning_rate=0.03,
        depth=6,
        loss_function='RMSE',
        verbose=200
    )
    
    catboost_model.fit(
        X_train, y_train,
        eval_set=(X_test, y_test),
        early_stopping_rounds=50
    )
    
    # Save model
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'solar_model_catboost.cbm')
    catboost_model.save_model(model_path)
    
    return catboost_model

def train_cnn(model, X_train, X_test, y_train, y_test):
    """Train CNN model with callbacks for better training"""
    
    # Create models directory if it doesn't exist
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(model_dir, exist_ok=True)
    
    # Define callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        ),
        ModelCheckpoint(
            filepath=os.path.join(model_dir, 'solar_model_cnn.keras'),
            monitor='val_loss',
            save_best_only=True
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=5,
            min_lr=0.0001
        )
    ]
    
    # Train the model
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=100,
        batch_size=32,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save training history
    plt.figure(figsize=(10, 6))
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss During Training')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.savefig(os.path.join(model_dir, 'training_history.png'))
    plt.close()
    
    return model, history

def train_and_save_models():
    try:
        # Load and preprocess data
        X, y = load_and_preprocess_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train CNN
        X_train_cnn = X_train_scaled.reshape((X_train_scaled.shape[0], X_train_scaled.shape[1], 1))
        X_test_cnn = X_test_scaled.reshape((X_test_scaled.shape[0], X_test_scaled.shape[1], 1))
        
        cnn_model = build_model((X_train_scaled.shape[1], 1))
        train_cnn(cnn_model, X_train_cnn, X_test_cnn, y_train, y_test)
        
        # Train CatBoost
        catboost_model = train_catboost_model(X_train, X_test, y_train, y_test)
        
        # Evaluate hybrid performance
        cnn_pred = cnn_model.predict(X_test_cnn)
        catboost_pred = catboost_model.predict(X_test)
        
        # Ensemble predictions
        hybrid_pred = 0.6 * cnn_pred.flatten() + 0.4 * catboost_pred
        
        print("\nHybrid Model Performance:")
        print(f"MAE: {mean_absolute_error(y_test, hybrid_pred):.2f}")
        print(f"R2 Score: {r2_score(y_test, hybrid_pred):.2f}")
        
    except Exception as e:
        print(f"Error during training: {str(e)}")
        raise

if __name__ == "__main__":
    train_and_save_models()