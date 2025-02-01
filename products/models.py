from django.db import models
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    is_plant = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PlantType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    status = models.BooleanField(default=True, help_text="Set to active or inactive.")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, limit_choices_to={'is_plant': True})

    class Meta:
        verbose_name_plural = "Plant Types"

    def __str__(self):
        return self.name


# PlantCategory Model
class PlantCategory(models.Model):
    SUNLIGHT_REQUIREMENT_CHOICES = [
        ('full_sun', 'Full Sun (6+ hours of direct sunlight)'),
        ('partial_sun', 'Partial Sun (4-6 hours of direct sunlight)'),
        ('partial_shade', 'Partial Shade (2-4 hours of direct sunlight)'),
        ('full_shade', 'Full Shade (less than 2 hours of direct sunlight)'),
    ]

    WATER_REQUIREMENT_CHOICES = [
        ('low', 'Low (water every 1-2 weeks)'),
        ('medium', 'Medium (water weekly)'),
        ('high', 'High (water multiple times a week)'),
    ]

    SOIL_TYPE_CHOICES = [
        ('loamy', 'Loamy (well-draining, nutrient-rich)'),
        ('sandy', 'Sandy (well-draining but nutrient-poor)'),
        ('clay', 'Clay (holds moisture but can be compacted)'),
        ('peat', 'Peat (rich in organic matter, retains moisture)'),
        ('silt', 'Silt (holds moisture and nutrients well)'),
    ]

    GROWTH_RATE_CHOICES = [
        ('slow', 'Slow (takes longer to mature)'),
        ('medium', 'Medium (average growth rate)'),
        ('fast', 'Fast (grows quickly)'),
    ]

    CLIMATE_SUITABILITY_CHOICES = [
        ('tropical', 'Tropical (hot and humid conditions)'),
        ('subtropical', 'Subtropical (warm with cooler winters)'),
        ('temperate', 'Temperate (moderate temperatures)'),
    ]

    SEASON_CHOICES = [
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('autumn', 'Autumn'),
        ('winter', 'Winter'),
    ]
    POT_SOIL_CHOICES = [
        ('pot', 'Select Pot'),
        ('soil', 'Select Soil'),
        ('both', 'Both'),
    ]

    plant_type = models.ForeignKey(
        PlantType, 
        on_delete=models.CASCADE, 
        related_name="categories", 
        blank=True, null=True  # Optional dropdown
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    pot_soil = models.CharField(
        max_length=10, choices=POT_SOIL_CHOICES, blank=True, null=True
    )
    sunlight_requirement = models.CharField(
        max_length=20, choices=SUNLIGHT_REQUIREMENT_CHOICES, blank=True, null=True
    )
    water_requirement = models.CharField(
        max_length=20, choices=WATER_REQUIREMENT_CHOICES, blank=True, null=True
    )
    soil_type = models.CharField(
        max_length=20, choices=SOIL_TYPE_CHOICES, blank=True, null=True
    )
    growth_rate = models.CharField(
        max_length=20, choices=GROWTH_RATE_CHOICES, blank=True, null=True
    )
    climate_suitability = models.CharField(
        max_length=20, choices=CLIMATE_SUITABILITY_CHOICES, blank=True, null=True
    )
    best_time_to_plant = models.CharField(
        max_length=20, choices=SEASON_CHOICES, blank=True, null=True
    )
    status = models.BooleanField(default=True, help_text="Set to active or inactive.")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Plant Categories"

    def __str__(self):
        return self.name



# Cultivation Method Model
class CultivationMethod(models.Model):
    plant_category = models.ForeignKey(
        PlantCategory, on_delete=models.CASCADE, related_name="cultivation_methods", 
        blank=True, null=True  # Optional dropdown
    )
    title = models.CharField(max_length=100)
    desc = models.TextField()
    steps = models.TextField()
    recommended_tools = models.TextField(blank=True, null=True)
    pit_size_height = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Height of the pit in meters", default=1.0
    )
    pit_size_width = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Width of the pit in meters", default=1.0
    )
    distance_between_plants = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Distance between plants in meters", default=1.0
    )
    watering_frequency = models.CharField(max_length=50)
    fertilization_guidelines = models.TextField(blank=True, null=True)
    common_issues = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True, help_text="Set to active or inactive.")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Cultivation Methods"

    def __str__(self):
        return f"Cultivation Method for {self.plant_category.name if self.plant_category else 'No Category'}: {self.title}"



# Product Model
class Product(models.Model):
    plant_type = models.ForeignKey(PlantType, on_delete=models.CASCADE, blank=True, null=True)
    plant_category = models.ForeignKey(PlantCategory, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image_1 = models.ImageField(upload_to='products/', blank=True, null=True)
    image_2 = models.ImageField(upload_to='products/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='products/', blank=True, null=True)
    status = models.BooleanField(default=True, help_text="Set to active or inactive.")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.name} ({self.plant_category.name if self.plant_category else 'No Category'})"


from django.utils.timezone import now
from datetime import timedelta

class Batch(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="batches")

    current_height = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    no_of_plants = models.PositiveIntegerField(default=1)
    discount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True, help_text="Set to active or inactive.")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Batches"

    def __str__(self):
        return f"{self.product.name} - Height: {self.current_height}"

    def save(self, *args, **kwargs):
        # Check if stock_quantity > 0 and 30 days have passed
        if self.stock_quantity > 0:
            # Calculate if 30 days have passed since updated_on
            if self.updated_on + timedelta(days=30) <= now():
                self.price += 10
                self.updated_on = now()  # Update the updated_on timestamp
        super().save(*args, **kwargs)

    def get_discounted_price(self):
        """Returns the price after applying the discount, if any."""
        if self.discount:
            discount_amount = (self.discount / 100) * self.price
            return self.price - discount_amount
        return self.price


# NonPlantProduct Model
class NonPlantProduct(models.Model):
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        limit_choices_to={'is_plant': False}, 
        related_name='non_plant_products'
    )
    brand = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    is_organic = models.BooleanField(default=False)
    usage = models.TextField()
    suitable_for_plants = models.TextField()
    image_1 = models.ImageField(upload_to='non_plant_products/')
    image_2 = models.ImageField(upload_to='non_plant_products/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='non_plant_products/', blank=True, null=True)
    status = models.BooleanField(default=True, help_text="Set to active or inactive.")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Non-Plant Products"

    def __str__(self):
        return self.name

    def clean(self):
        if self.category.is_plant:
            raise ValidationError("Category for Non-Plant Product cannot be a plant category.")



class Wishlist(models.Model):
    email = models.ForeignKey('userauths.Login', on_delete=models.CASCADE, null=True, blank=True)  # Referencing Login model
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True)  # Nullable foreign key
    added_on = models.DateTimeField(auto_now_add=True)  # When the item was added

    def __str__(self):
        return f"{self.email.email} - {self.batch.product.name if self.batch else 'No Batch'} - {self.batch.price if self.batch else 'No Price'}"
