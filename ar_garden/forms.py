from django import forms
from .models import FieldImage, UserPlantSelection, PlantType

class FieldImageForm(forms.ModelForm):
    class Meta:
        model = FieldImage
        fields = ['image', 'width', 'length']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': True
            }),
            'width': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0.1',
                'required': True,
                'placeholder': 'Enter field width'
            }),
            'length': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0.1',
                'required': True,
                'placeholder': 'Enter field length'
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            raise forms.ValidationError('Please select an image file')
        if not image.content_type.startswith('image/'):
            raise forms.ValidationError('Please upload a valid image file')
        return image

    def clean(self):
        cleaned_data = super().clean()
        width = cleaned_data.get('width')
        length = cleaned_data.get('length')

        if width is not None and width <= 0:
            self.add_error('width', 'Width must be greater than 0')
        if length is not None and length <= 0:
            self.add_error('length', 'Length must be greater than 0')

        return cleaned_data

class PlantSelectionForm(forms.ModelForm):
    class Meta:
        model = UserPlantSelection
        fields = ['plant', 'x_position', 'y_position', 'rotation']
        widgets = {
            'x_position': forms.HiddenInput(),
            'y_position': forms.HiddenInput(),
            'rotation': forms.HiddenInput(),
        }
# ar_garden/forms.py
from django import forms
from .models import PlantType

class PlantTypeForm(forms.ModelForm):
    class Meta:
        model = PlantType
        fields = ['name', 'icon', 'model_3d', 'min_spacing', 'height']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter plant name'
            }),
            'icon': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'model_3d': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.glb,.gltf'
            }),
            'min_spacing': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0.1',
                'placeholder': 'Enter minimum spacing in meters'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0.1',
                'placeholder': 'Enter plant height in meters'
            })
        }