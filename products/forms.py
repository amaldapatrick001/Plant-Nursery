from django import forms
from .models import Product, Category
from django.core.exceptions import ValidationError

from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']

        

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'product_name', 'price', 'stock_quantity', 
            'sunlight_requirement', 'water_need', 'climate_compatibility', 
            'growth_rate', 'soil_type', 'flowering_season', 
            'height_range', 'description', 'image', 'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'sunlight_requirement': forms.Select(attrs={'class': 'form-control'}),
            'water_need': forms.Select(attrs={'class': 'form-control'}),
            'climate_compatibility': forms.Select(attrs={'class': 'form-control'}),
            'growth_rate': forms.Select(attrs={'class': 'form-control'}),
            'soil_type': forms.Select(attrs={'class': 'form-control'}),
            'flowering_season': forms.Select(attrs={'class': 'form-control'}),
            'height_range': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Validate file extension
            valid_extensions = ['.jpg', '.jpeg', '.jpe', '.png']
            extension = os.path.splitext(image.name)[1].lower()
            if extension not in valid_extensions:
                raise ValidationError('Only JPG, JPEG, JPE, and PNG images are allowed.')

            # Validate file size (e.g., max 5MB)
            max_size = 5 * 1024 * 1024  # 5MB
            if image.size > max_size:
                raise ValidationError('Image size must be under 5MB.')

        return image
