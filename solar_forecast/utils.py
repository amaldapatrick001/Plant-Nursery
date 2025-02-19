import requests

NASA_API_URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"
OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_API_KEY = "0acebc8791d9539d4e0b68f7262d10b6"

def get_weather_data(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "parameters": "T2M,RH2M,CLRSKY_SFC_SW_DWN,WS2M,PRECTOTCORR",
        "community": "RE",
        "format": "JSON",
    }
    response = requests.get(NASA_API_URL, params=params)
    data = response.json()

    # Extract necessary values
    temp = data['properties']['parameter']['T2M'][-1]
    humidity = data['properties']['parameter']['RH2M'][-1]
    solar_radiation = data['properties']['parameter']['CLRSKY_SFC_SW_DWN'][-1]

    return temp, humidity, solar_radiation

def get_wind_precipitation(city):
    params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    response = requests.get(OPENWEATHER_API_URL, params=params)
    data = response.json()

    wind_speed = data['wind']['speed']
    precipitation = data.get('rain', {}).get('1h', 0)  # If no rain, default to 0

    return wind_speed, precipitation

def calculate_theoretical_solar_radiation(temp, humidity, wind_speed, precipitation, cloud_coverage):
    # Enhanced theoretical model
    max_radiation = 1000  # Maximum possible radiation at sea level
    cloud_factor = 1 - (cloud_coverage / 100)
    temp_factor = 1 + ((temp - 25) / 100)  # Temperature adjustment
    humidity_factor = 1 - (humidity / 200)  # Humidity adjustment
    wind_factor = 1 - (wind_speed / 20)  # Wind adjustment
    
    theoretical_radiation = max_radiation * cloud_factor * temp_factor * humidity_factor * wind_factor
    
    # Enhanced precipitation adjustment
    if precipitation > 0:
        rain_factor = 1 - (precipitation / 25)  # More sensitive to rain
        theoretical_radiation *= max(0.2, rain_factor)  # Minimum 20% radiation even in heavy rain
        
    return max(0, min(1200, theoretical_radiation))