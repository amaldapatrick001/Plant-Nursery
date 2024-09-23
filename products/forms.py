from django import forms
from .models import Product, Category
from django.core.exceptions import ValidationError

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter category description'}),
        }

    def clean_category_name(self):
        category_name = self.cleaned_data.get('category_name')
        if len(category_name) < 3:
            raise ValidationError('Category name must be at least 3 characters long.')
        return category_name

    def clean_description(self):
        description = self.cleaned_data.get('description')
        word_count = len(description.split())
        if word_count > 100:
            raise ValidationError('Description must not exceed 100 words.')
        return description



import os

# forms.py
from django import forms
from .models import Product
from django.core.exceptions import ValidationError

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

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        if price > 10000:
            raise forms.ValidationError("Price cannot exceed 10,000.")
        return price

    def clean_stock_quantity(self):
        stock_quantity = self.cleaned_data.get('stock_quantity')
        if stock_quantity < 0:
            raise forms.ValidationError("Stock quantity cannot be negative.")
        if stock_quantity > 1000:
            raise forms.ValidationError("Stock quantity cannot exceed 1,000.")
        return stock_quantity

    def clean_product_name(self):
        product_name = self.cleaned_data.get('product_name')
        if not product_name or len(product_name.strip()) == 0:
            raise forms.ValidationError("Product name cannot be empty.")
        if len(product_name) < 3:
            raise forms.ValidationError("Product name must be at least 3 characters long.")
        return product_name

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description) > 1000:
            raise forms.ValidationError("Description cannot exceed 1000 characters.")
        return description

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
