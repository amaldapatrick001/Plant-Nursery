import os
import requests
import pandas as pd
import time
import numpy as np
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import signal
import sys

# 📌 List of More Locations in Each District (Cities, Towns & Small Areas)
LOCATIONS = {
    "Kottayam": [
        ("Kottayam", 9.5916, 76.5222),
        ("Pala", 9.7000, 76.6833),
        ("Changanassery", 9.4500, 76.5500),
        ("Ettumanoor", 9.6667, 76.5667),
        ("Vaikom", 9.7500, 76.4000),
        ("Kumarakom", 9.5500, 76.5000),  # Tourism & agriculture
        ("Kothamangalam", 10.0000, 76.6000),
        ("Thodupuzha", 9.8920, 76.7180),
        ("Kangirappally", 9.5000, 76.6000),
        ("Manarcad", 9.5800, 76.5200),  # Pilgrimage site
        ("Puthuppally", 9.5800, 76.5400),  # Rubber plantation area
        ("Uzhavoor", 9.7833, 76.6333),  # Hilly agricultural region
    ],
    "Thrissur": [
        ("Thrissur", 10.5276, 76.2144),
        ("Chalakudy", 10.3000, 76.3300),
        ("Kodungallur", 10.2200, 76.1800),
        ("Guruvayur", 10.6000, 76.0500),  # Famous for Guruvayur Temple
        ("Irinjalakuda", 10.3500, 76.2200),
        ("Kunnamkulam", 10.6500, 76.0700),
        ("Koduvally", 10.1000, 76.2200),
        ("Athirappilly", 10.2840, 76.5698),  # Tourist waterfall location
        ("Wadakkanchery", 10.6575, 76.1265),  # Agricultural belt
        ("Mala", 10.2667, 76.2167),
    ],
    "Ranni": [
        ("Ranni", 9.3822, 76.8028),
        ("Vadasserikkara", 9.3900, 76.7800),
        ("Perunad", 9.4300, 76.8100),
        ("Kozhencherry", 9.3900, 76.7000),
        ("Thannithodu", 9.4200, 76.8200),
        ("Koduvally", 10.0000, 76.6000),
        ("Pathanamthitta", 9.2640, 76.7872),  # Pilgrim site
        ("Konni", 9.2330, 76.9660),  # Known for elephant training center
        ("Mallappally", 9.4389, 76.6683),
    ],
    "Ernakulam": [
        ("Ernakulam", 9.9816, 76.2999),
        ("Aluva", 10.1100, 76.3500),
        ("Angamaly", 10.2000, 76.3900),
        ("Kochi", 9.9700, 76.2900),  # Major city & port
        ("Perumbavoor", 10.1100, 76.4800),
        ("Piravom", 9.8000, 76.5000),  # Rubber & spice plantations
        ("Muvattupuzha", 9.9771, 76.5781),  # Commercial town
        ("Kakkanad", 9.9820, 76.3465),  # IT hub (Smart City)
        ("Paravur", 10.1450, 76.2167),  # Backwaters tourism
    ],
    "Idukki": [
        ("Idukki", 9.8562, 76.9784),
        ("Munnar", 10.0892, 77.0595),  # Tea plantation area
        ("Thodupuzha", 9.8920, 76.7180),
        ("Kattappana", 9.7519, 77.1211),
        ("Kumily", 9.6048, 77.1576),  # Gateway to Periyar Tiger Reserve
        ("Thekkady", 9.6027, 77.1681),  # Wildlife tourism
        ("Vagamon", 9.6858, 76.9045),  # Hill station
        ("Ramakkalmedu", 9.7248, 77.1456),  # Wind farm & tourism
        ("Peermade", 9.5679, 77.0357),  # Spices and tea estates
    ],
}

# 📌 API Configurations
NASA_API_URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"
OPENWEATHER_API_KEY = "0acebc8791d9539d4e0b68f7262d10b6"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Add signal handler for graceful shutdown
def signal_handler(sig, frame):
    print('\nShutting down gracefully...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def fetch_nasa_data(lat, lon):
    """Fetches solar radiation data from NASA POWER API"""
    params = {
        "latitude": lat, "longitude": lon,
        "parameters": "ALLSKY_SFC_SW_DWN,T2M,RH2M,WS2M,PRECTOTCORR",
        "community": "RE", "start": "20240101", "end": "20240210", "format": "JSON"
    }
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,  # number of retries
        backoff_factor=1,  # wait 1, 2, 4 seconds between retries
        status_forcelist=[500, 502, 503, 504]  # HTTP status codes to retry on
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    
    try:
        with requests.Session() as session:
            session.mount("https://", adapter)
            session.mount("http://", adapter)
            
            response = session.get(
                NASA_API_URL,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching NASA data: {str(e)}")
        return None
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)

def fetch_weather_data(lat, lon):
    """Fetches real-time weather data from OpenWeatherMap"""
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        with requests.Session() as session:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "cloud_coverage": data["clouds"]["all"],
                "precipitation": data.get("rain", {}).get("1h", 0)
            }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {str(e)}")
        return None
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)

# 📌 Collect and Save Data
for district, towns in LOCATIONS.items():
    for town_name, lat, lon in towns:
        nasa_data = fetch_nasa_data(lat, lon)
        weather_data = fetch_weather_data(lat, lon)
        if not nasa_data or not weather_data:
            continue
        df = pd.DataFrame({
            "timestamp": list(nasa_data["properties"]["parameter"]["T2M"].keys()),
            "temperature": list(nasa_data["properties"]["parameter"]["T2M"].values()),
            "humidity": list(nasa_data["properties"]["parameter"]["RH2M"].values()),
            "wind_speed": list(nasa_data["properties"]["parameter"]["WS2M"].values()),
            "precipitation": list(nasa_data["properties"]["parameter"]["PRECTOTCORR"].values()),
            "solar_radiation": list(nasa_data["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"].values()),
            "cloud_coverage": weather_data["cloud_coverage"],
        })

        # Handle missing values by imputing with column means (only numeric columns)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

        # Convert timestamp to string to ensure correct parsing later
        df['timestamp'] = df['timestamp'].astype(str)

        # Define the start and end datetime objects
        start_datetime = pd.to_datetime("2024010100", format='%Y%m%d%H')
        end_datetime = pd.to_datetime("2024021000", format='%Y%m%d%H')

        # Convert 'timestamp' to datetime for filtering
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H', errors='coerce')

        # Drop rows with invalid timestamps
        df = df.dropna(subset=['timestamp'])

        # Filter rows within the desired date range
        df = df[(df['timestamp'] >= start_datetime) & (df['timestamp'] <= end_datetime)]

        # Convert 'timestamp' back to string if necessary
        df['timestamp'] = df['timestamp'].dt.strftime('%Y%m%d%H')

        df.to_csv(os.path.join(DATA_DIR, f"{town_name}_solar_data.csv"), index=False)

if __name__ == "__main__":
    try:
        nasa_data = fetch_nasa_data(lat, lon)
        if nasa_data:
            # Process NASA data
            pass
            
        weather_data = fetch_weather_data(lat, lon)
        if weather_data:
            # Process weather data
            pass
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
