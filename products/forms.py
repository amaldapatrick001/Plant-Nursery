<<<<<<< HEAD
from django import forms
from .models import Product, Category
from django import forms
from django.core.exceptions import ValidationError
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']

        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter category description'}),
        }

    # Custom validation for category_name
    def clean_category_name(self):
        category_name = self.cleaned_data.get('category_name')
        if len(category_name) < 3:
            raise ValidationError('Category name must be at least 3 characters long.')
        return category_name

    # Custom validation for description
    def clean_description(self):
        description = self.cleaned_data.get('description')
        word_count = len(description.split())
        if word_count > 100:
            raise ValidationError('Description must not exceed 100 words.')
        return description

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True)
    sunlight_requirement = forms.ChoiceField(choices=Product.SunlightRequirement.choices, required=True)
    water_need = forms.ChoiceField(choices=Product.WaterNeed.choices, required=True)
    climate_compatibility = forms.ChoiceField(choices=Product.ClimateCompatibility.choices, required=True)
    growth_rate = forms.ChoiceField(choices=Product.GrowthRate.choices, required=True)
    soil_type = forms.ChoiceField(choices=Product.SoilType.choices, required=True)
    flowering_season = forms.ChoiceField(choices=Product.FloweringSeason.choices, required=True)
    height_range = forms.ChoiceField(choices=Product.HeightRange.choices, required=True)


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
=======
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
>>>>>>> origin/main
