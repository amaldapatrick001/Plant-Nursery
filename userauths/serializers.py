from rest_framework import serializers
from .models import DeliveryPersonnel

class LocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPersonnel
        fields = ['current_latitude', 'current_longitude'] 