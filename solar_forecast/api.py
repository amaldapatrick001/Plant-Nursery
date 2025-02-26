from rest_framework.decorators import api_view
from rest_framework.response import Response
from .predict import predict_solar_radiation
import os
import pandas as pd

DATA_DIR = "F:/mp2/PlantNursery/solar_forecast/data"

@api_view(['GET'])
def get_solar_forecast(request):
    town = request.GET.get("town")
    if not town:
        return Response({"error": "Please provide a town name"}, status=400)

    try:
        file_path = os.path.join(DATA_DIR, f"{town}_solar_data.csv")
        if not os.path.exists(file_path):
            return Response({"error": f"Data for {town} not found"}, status=404)

        df = pd.read_csv(file_path)
        latest_data = df.iloc[-1].to_dict()
        
        # Add prediction using hybrid model
        prediction = predict_solar_radiation(
            latest_data['temperature'],
            latest_data['humidity'],
            latest_data['wind_speed'],
            latest_data['precipitation'],
            latest_data['cloud_coverage']
        )
        
        latest_data['predicted_radiation'] = prediction
        return Response(latest_data)
        
    except Exception as e:
        return Response({"error": str(e)}, status=500)
