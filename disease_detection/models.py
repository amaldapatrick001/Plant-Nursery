# disease_detection/models.py

from django.db import models

class PlantImage(models.Model):
    image = models.ImageField(upload_to='plant_images/')
    disease_detected = models.CharField(max_length=255, blank=True, null=True)
    confidence = models.FloatField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.disease_detected} ({self.confidence:.2f}% confidence)"
