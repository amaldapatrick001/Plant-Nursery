# disease_detection/serializers.py

from rest_framework import serializers
from .models import PlantImage

class PlantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantImage
        fields = [
            'id', 'image', 'plant_name', 'plant_confidence',
            'disease_detected', 'confidence', 'treatment_suggestions',
            'uploaded_at'
        ]
