from django.db import models

class SolarForecast(models.Model):
    location = models.CharField(max_length=255)
    date = models.DateField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    cloud_volume = models.FloatField()
    wind_speed = models.FloatField()
    precipitation = models.FloatField()
    solar_radiation = models.FloatField()  # Actual solar radiation
    predicted_radiation = models.FloatField(null=True, blank=True)  # Prediction output

    def __str__(self):
        return f"{self.location} - {self.date}"
