# disease_detection/forms.py

from django import forms
from .models import PlantImage

class PlantImageForm(forms.ModelForm):
    class Meta:
        model = PlantImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }
