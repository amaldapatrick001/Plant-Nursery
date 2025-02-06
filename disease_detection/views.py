# disease_detection/views.py

from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import PlantImage
from .serializers import PlantImageSerializer
from .forms import PlantImageForm
from .ml_model import identify_plant_and_disease

class PlantDiseaseDetectionView(APIView):
    """
    REST API View to handle image uploads and return disease prediction.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_serializer = PlantImageSerializer(data=request.data)

        if file_serializer.is_valid():
            plant_image = file_serializer.save()

            # Run the prediction model with enhanced identification
            results = identify_plant_and_disease(plant_image.image.path)

            # Update the database with prediction results
            plant_image.plant_name = results['plant_name']
            plant_image.plant_confidence = results['plant_confidence']
            plant_image.disease_detected = results['disease_name']
            plant_image.confidence = results['disease_confidence']
            plant_image.treatment_suggestions = '\n'.join(results['treatment_suggestions'])
            plant_image.save()

            return Response({
                "message": "Prediction successful!",
                "id": plant_image.id,
                "plant_name": results['plant_name'],
                "plant_confidence": results['plant_confidence'],
                "disease_detected": results['disease_name'],
                "disease_confidence": results['disease_confidence'],
                "treatment_suggestions": results['treatment_suggestions'],
                "image_url": request.build_absolute_uri(plant_image.image.url)
            }, status=status.HTTP_201_CREATED)

        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def upload_image_view(request):
    """
    Web-based view for uploading images and displaying predictions.
    """
    if request.method == 'POST':
        form = PlantImageForm(request.POST, request.FILES)
        if form.is_valid():
            plant_image = form.save()  # Save the uploaded image
            
            # Run prediction with enhanced identification
            results = identify_plant_and_disease(plant_image.image.path)
            
            # Update the database with results
            plant_image.plant_name = results['plant_name']
            plant_image.plant_confidence = results['plant_confidence']
            plant_image.disease_detected = results['disease_name']
            plant_image.confidence = results['disease_confidence']
            plant_image.treatment_suggestions = '\n'.join(results['treatment_suggestions'])
            plant_image.save()
            
            return render(request, 'disease_detection/result.html', {
                'plant_image': plant_image,
                'treatments': results['treatment_suggestions']
            })

    else:
        form = PlantImageForm()

    return render(request, 'disease_detection/upload.html', {'form': form})
