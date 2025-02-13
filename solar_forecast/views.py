from django.shortcuts import render
from .predict import predict_solar_radiation
import pandas as pd
import os
from datetime import datetime, timedelta

def solar_forecast_view(request):
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    
    # Get list of available locations from data files
    locations = [f.split('_solar_data.csv')[0].split('/')[-1] 
                for f in os.listdir(DATA_DIR) 
                if f.endswith('_solar_data.csv')]

    selected_location = request.GET.get('location', locations[0] if locations else None)
    
    context = {
        'locations': locations,
        'selected_location': selected_location,
    }

    if selected_location:
        try:
            # Read historical data
            file_path = os.path.join(DATA_DIR, f"{selected_location}_solar_data.csv")
            df = pd.read_csv(file_path)
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H', errors='coerce')
            
            # Optionally, handle rows where parsing failed
            df = df.dropna(subset=['timestamp'])
            
            # Get today's data (most recent)
            latest_data = df.iloc[-1].to_dict()
            
            # Ensure we have non-zero values or use average
            if latest_data['solar_radiation'] == 0:
                latest_data['solar_radiation'] = df['solar_radiation'].mean()
            if latest_data['precipitation'] == 0:
                latest_data['precipitation'] = df['precipitation'].mean()

            # Predict tomorrow's data
            tomorrow_prediction = predict_solar_radiation(
                latest_data['temperature'],
                latest_data['humidity'],
                latest_data['wind_speed'],
                latest_data['precipitation'],
                latest_data['cloud_coverage']
            )

            # Format dates
            today = datetime.now().strftime('%Y-%m-%d')
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

            context.update({
                'today_data': {
                    'date': today,
                    'temperature': round(latest_data['temperature'], 2),
                    'humidity': round(latest_data['humidity'], 2),
                    'wind_speed': round(latest_data['wind_speed'], 2),
                    'precipitation': round(float(latest_data['precipitation']), 2),
                    'solar_radiation': round(float(latest_data['solar_radiation']), 2),
                    'cloud_coverage': round(latest_data['cloud_coverage'], 2),
                },
                'tomorrow_prediction': {
                    'date': tomorrow,
                    'solar_radiation': tomorrow_prediction
                }
            })
            
        except Exception as e:
            print(f"Error processing data for {selected_location}: {str(e)}")
            context['error'] = f"Error processing data for {selected_location}"

    return render(request, 'solar_forecast/forecast.html', context)
