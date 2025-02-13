from rest_framework.decorators import api_view
from rest_framework.response import Response
import os
import pandas as pd

DATA_DIR = "F:/mp2/PlantNursery/solar_forecast/data"

@api_view(['GET'])
def get_solar_forecast(request):
    town = request.GET.get("town")
    if not town:
        return Response({"error": "Please provide a town name"}, status=400)

    file_path = os.path.join(DATA_DIR, f"{town}_solar_data.csv")
    if not os.path.exists(file_path):
        return Response({"error": f"Data for {town} not found"}, status=404)

    df = pd.read_csv(file_path)
    latest_data = df.iloc[-1].to_dict()
    return Response(latest_data)
