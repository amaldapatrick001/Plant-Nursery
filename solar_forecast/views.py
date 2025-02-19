from django.shortcuts import render
from .predict import predict_solar_radiation
import pandas as pd
import os
from datetime import datetime, timedelta
from django.http import JsonResponse

def get_plant_care_recommendations(solar_radiation, plant_data, is_tomorrow=False):
    """Get plant care recommendations based on solar radiation levels"""
    recommendations = []
    
    for _, plant in plant_data.iterrows():
        recommendation = {
            'name': plant['Plant Name'],
            'scientific_name': plant['Scientific Name'],
            'category': plant['Category'],
            'min_radiation': float(plant['Min Radiation (W/m²)']),
            'max_radiation': float(plant['Max Radiation (W/m²)']),
            'status': 'normal',
            'is_tomorrow': is_tomorrow
        }
        
        if solar_radiation < plant['Min Radiation (W/m²)']:
            recommendation.update({
                'care': plant['Low Radiation Care'],
                'status': 'low'
            })
        elif solar_radiation > plant['Max Radiation (W/m²)']:
            recommendation.update({
                'care': plant['High Radiation Care'],
                'status': 'high'
            })
        else:
            recommendation.update({
                'care': plant['Normal Radiation Care'],
                'status': 'normal'
            })
        
        recommendations.append(recommendation)
    
    return recommendations

def get_plant_details(plant_data, search_term=None):
    """Get plant details with optional search filtering"""
    plants = []
    
    for _, plant in plant_data.iterrows():
        plant_info = {
            'name': plant['Plant Name'],
            'scientific_name': plant['Scientific Name'],
            'category': plant['Category'],
            'min_radiation': plant['Min Radiation (W/m²)'],
            'max_radiation': plant['Max Radiation (W/m²)'],
            'normal_care': plant['Normal Radiation Care'],
            'low_care': plant['Low Radiation Care'],
            'high_care': plant['High Radiation Care']
        }
        
        if search_term:
            if (search_term.lower() in plant_info['name'].lower() or 
                search_term.lower() in plant_info['scientific_name'].lower()):
                plants.append(plant_info)
        else:
            plants.append(plant_info)
    
    return plants

def solar_forecast_view(request):
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    
    # Get the view type from AJAX request or default to 'today'
    view_type = request.GET.get('view_type', 'today')
    
    # Load plant data
    plant_data = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                            'Kerala_Plant_Data_Updated.csv'))
    
    # Get list of available locations from data files
    locations = [f.split('_solar_data.csv')[0].split('/')[-1] 
                for f in os.listdir(DATA_DIR) 
                if f.endswith('_solar_data.csv')]

    selected_location = request.GET.get('location', locations[0] if locations else None)
    selected_category = request.GET.get('category', 'All')
    
    # Add search functionality
    search_term = request.GET.get('search', '')
    
    context = {
        'locations': locations,
        'selected_location': selected_location,
        'categories': ['All'] + sorted(plant_data['Category'].unique().tolist()),
        'selected_category': selected_category,
        'search_term': search_term
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

            # Filter plants by category if selected
            if selected_category != 'All':
                plant_data = plant_data[plant_data['Category'] == selected_category]

            # Get care recommendations based on view type
            if view_type == 'today':
                recommendations = get_plant_care_recommendations(
                    latest_data['solar_radiation'], 
                    plant_data,
                    is_tomorrow=False
                )
            else:  # tomorrow
                recommendations = get_plant_care_recommendations(
                    tomorrow_prediction, 
                    plant_data,
                    is_tomorrow=True
                )

            # Get plant details with search
            plant_details = get_plant_details(plant_data, search_term)
            
            # Update context with recommendations
            context.update({
                'recommendations': recommendations,
                'view_type': view_type,
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
                },
                'plant_details': plant_details
            })
            
            # Update recommendations to include radiation ranges
            for rec in recommendations:
                plant_info = plant_data[plant_data['Plant Name'] == rec['name']].iloc[0]
                rec.update({
                    'min_radiation': plant_info['Min Radiation (W/m²)'],
                    'max_radiation': plant_info['Max Radiation (W/m²)']
                })

            # If it's an AJAX request, return only the recommendations
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'recommendations': recommendations,
                    'view_type': view_type
                })

        except Exception as e:
            print(f"Error processing data for {selected_location}: {str(e)}")
            context['error'] = f"Error processing data for {selected_location}"

    return render(request, 'solar_forecast/forecast.html', context)
