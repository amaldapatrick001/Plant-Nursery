# disease_detection/urls.py

from django.urls import path
from .views import PlantDiseaseDetectionView,upload_image_view
app_name = 'disease_detection'
urlpatterns = [
    path('api/predict/', PlantDiseaseDetectionView.as_view(), name='predict_disease'),
    path('upload/', upload_image_view, name='upload_image'),
]