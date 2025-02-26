from rest_framework import serializers
from .models import Plant, UserLayout

class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = ['id', 'name', 'image', 'min_spacing_m']

class UserLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLayout
        fields = ['id', 'name', 'plot_width', 'plot_length', 'plant_positions', 'created_at', 'updated_at']