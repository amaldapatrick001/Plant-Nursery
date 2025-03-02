from django import forms
from .models import Plant, UserLayout

class LayoutUploadForm(forms.ModelForm):
    class Meta:
        model = UserLayout
        fields = ['layout_name', 'plot_image', 'plot_width', 'plot_length']
        widgets = {
            'layout_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter layout name'
            }),
            'plot_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'plot_width': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Width in meters',
                'step': '0.1'
            }),
            'plot_length': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Length in meters',
                'step': '0.1'
            })
        }

class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = ['name', 'image', 'min_spacing_m', 'max_spacing_m']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'min_spacing_m': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_spacing_m': forms.NumberInput(attrs={'class': 'form-control'}),
        }
from django import forms
from .models import UserLayout

class UserLayoutForm(forms.ModelForm):
    class Meta:
        model = UserLayout
        fields = ['layout_name', 'plot_width', 'plot_length', 'background_type', 'background_color', 'plot_image']
        widgets = {
            'background_color': forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plot_image'].required = False
        self.fields['background_color'].required = False
        # Add help text
        self.fields['background_type'].help_text = "Choose 'Image' to upload a background image or 'Color' to set a background color"

    def clean(self):
        cleaned_data = super().clean()
        background_type = cleaned_data.get('background_type')
        plot_image = cleaned_data.get('plot_image')
        background_color = cleaned_data.get('background_color')

        if background_type == 'image':
            if not plot_image and not self.instance.plot_image:
                self.add_error('plot_image', "Plot image is required when background type is 'image'.")
        elif background_type == 'color':
            if not background_color:
                self.add_error('background_color', "Background color is required when background type is 'color'.")

        return cleaned_data