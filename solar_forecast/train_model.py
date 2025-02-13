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

def train_and_save_models():
    """Train the model and save if performance meets criteria"""
    try:
        # Load and preprocess data
        X, y = load_and_preprocess_data()
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale the features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Reshape data for CNN
        X_train_reshaped = X_train_scaled.reshape((X_train_scaled.shape[0], X_train_scaled.shape[1], 1))
        X_test_reshaped = X_test_scaled.reshape((X_test_scaled.shape[0], X_test_scaled.shape[1], 1))
        
        # Build model
        model = build_model((X_train_scaled.shape[1], 1))
        
        # Setup model directory
        model_dir = os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(model_dir, exist_ok=True)
        
        # Define callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=20,
                restore_best_weights=True,
                verbose=1
            ),
            ModelCheckpoint(
                os.path.join(model_dir, 'solar_model.keras'),
                monitor='val_loss',
                save_best_only=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=10,
                min_lr=0.00001,
                verbose=1
            )
        ]
        
        # Train model
        history = model.fit(
            X_train_reshaped,
            y_train,
            validation_data=(X_test_reshaped, y_test),
            epochs=100,
            batch_size=32,
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate model
        test_loss, test_mae = model.evaluate(X_test_reshaped, y_test, verbose=0)
        print(f"\nTest MAE: {test_mae:.2f} W/m²")
        
        # Plot training history
        plt.figure(figsize=(12, 4))
        
        # Plot loss
        plt.subplot(1, 2, 1)
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        # Plot MAE
        plt.subplot(1, 2, 2)
        plt.plot(history.history['mae'], label='Training MAE')
        plt.plot(history.history['val_mae'], label='Validation MAE')
        plt.title('Model MAE')
        plt.xlabel('Epoch')
        plt.ylabel('MAE (W/m²)')
        plt.legend()
        
        # Save plot
        plt.tight_layout()
        plt.savefig(os.path.join(model_dir, 'training_history.png'))
        plt.close()
        
        print("\nTraining completed successfully!")
        print(f"Model saved to: {os.path.join(model_dir, 'solar_model.keras')}")
        print(f"Training history plot saved to: {os.path.join(model_dir, 'training_history.png')}")
        
    except Exception as e:
        print(f"Error during training: {str(e)}")
        raise

if __name__ == "__main__":
    train_and_save_models()