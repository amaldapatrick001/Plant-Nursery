from django.apps import AppConfig
import threading
import os

class SolarForecastConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "solar_forecast"

    def ready(self):
        """Runs when Django starts. Fetches data in the background."""
        def fetch_data():
            os.system("python solar_forecast/fetch_solar_data.py")  # Run fetch script

        thread = threading.Thread(target=fetch_data)
        thread.start()  # Runs in the background
