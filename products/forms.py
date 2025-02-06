from django import forms
from .models import Category, PlantType, PlantCategory, Product, Batch, CultivationMethod, NonPlantProduct


# Category Form
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_plant', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'status': forms.CheckboxInput(),
        }


# PlantType Form
class PlantTypeForm(forms.ModelForm):
    class Meta:
        model = PlantType
        fields = ['name', 'description', 'status', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'status': forms.CheckboxInput(),
        }


# PlantCategory Form

class PlantCategoryForm(forms.ModelForm):
    class Meta:
        model = PlantCategory
        fields = [
            'plant_type', 'name', 'description', 'pot_soil',
            'sunlight_requirement', 'water_requirement',
            'soil_type', 'growth_rate', 'climate_suitability',
            'best_time_to_plant'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'pot_soil': forms.Select(),  # Use Select widget for pot_soil
            'sunlight_requirement': forms.Select(),
            'water_requirement': forms.Select(),
            'soil_type': forms.Select(),
            'growth_rate': forms.Select(),
            'climate_suitability': forms.Select(),
            'best_time_to_plant': forms.Select(),
            'status': forms.CheckboxInput(),
        }

# CultivationMethod Form

class CultivationMethodForm(forms.ModelForm):
    class Meta:
        model = CultivationMethod
        fields = [
            'plant_category', 'title', 'desc', 'steps',
            'recommended_tools', 'pit_size_height',
            'pit_size_width', 'distance_between_plants',
            'watering_frequency', 'fertilization_guidelines',
            'common_issues'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set plant_category as not required
        self.fields['plant_category'].required = False



# Product Form
# forms.py
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['plant_type', 'plant_category', 'name', 'description', 'image_1', 'image_2', 'image_3', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    # Override init to make images non-mandatory
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['image_1'].required = False
        self.fields['image_2'].required = False
        self.fields['image_3'].required = False

# Batch Form
class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['product', 'current_height', 'price', 'stock_quantity', 'discount', 'short_description','no_of_plants']

widgets = {
            'short_description': forms.Textarea(attrs={'rows': 2}),
            'discount': forms.NumberInput(),  # Added widget for discount
            'status': forms.CheckboxInput(),
        }
def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the status field to True by default
        self.instance.status = True  # This will set the status to True when creating a new batch




# NonPlantProduct Form
class NonPlantProductForm(forms.ModelForm):
    class Meta:
        model = NonPlantProduct
        fields = [
            'category', 'brand', 'name', 'description', 'price', 'stock_quantity',
            'is_organic', 'usage', 'suitable_for_plants', 'image_1', 'image_2', 'image_3', 'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'status': forms.CheckboxInput(),
        }

    # Clean method to validate that category is non-plant
    def clean_category(self):
        category = self.cleaned_data.get('category')
        if category.is_plant:
            raise forms.ValidationError("Category for Non-Plant Product cannot be a plant category.")
        return category

