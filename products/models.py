from django.db import models

class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.category_name

class Product(models.Model):
    class SunlightRequirement(models.TextChoices):
        FULL_SUN = 'Full Sun', 'Full Sun'
        PARTIAL_SHADE = 'Partial Shade', 'Partial Shade'
        FULL_SHADE = 'Full Shade', 'Full Shade'

    class WaterNeed(models.TextChoices):
        LOW = 'Low', 'Low'
        MEDIUM = 'Medium', 'Medium'
        HIGH = 'High', 'High'

    class ClimateCompatibility(models.TextChoices):
        TROPICAL = 'Tropical', 'Tropical'
        SUBTROPICAL = 'Subtropical', 'Subtropical'
        TEMPERATE = 'Temperate', 'Temperate'
        ARID = 'Arid', 'Arid'

    class GrowthRate(models.TextChoices):
        SLOW = 'Slow', 'Slow'
        MODERATE = 'Moderate', 'Moderate'
        FAST = 'Fast', 'Fast'

    class SoilType(models.TextChoices):
        SANDY = 'Sandy', 'Sandy'
        LOAMY = 'Loamy', 'Loamy'
        CLAY = 'Clay', 'Clay'
        PEATY = 'Peaty', 'Peaty'
        SILTY = 'Silty', 'Silty'

    class FloweringSeason(models.TextChoices):
        SPRING = 'Spring', 'Spring'
        SUMMER = 'Summer', 'Summer'
        AUTUMN = 'Autumn', 'Autumn'
        WINTER = 'Winter', 'Winter'

    class HeightRange(models.TextChoices):
        SHORT = 'Short', 'Short'
        MEDIUM = 'Medium', 'Medium'
        TALL = 'Tall', 'Tall'

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    sunlight_requirement = models.CharField(
        max_length=20, choices=SunlightRequirement.choices
    )
    water_need = models.CharField(
        max_length=10, choices=WaterNeed.choices
    )
    climate_compatibility = models.CharField(
        max_length=15, choices=ClimateCompatibility.choices
    )
    growth_rate = models.CharField(
        max_length=10, choices=GrowthRate.choices
    )
    soil_type = models.CharField(
        max_length=10, choices=SoilType.choices
    )
    flowering_season = models.CharField(
        max_length=10, choices=FloweringSeason.choices
    )
    height_range = models.CharField(
        max_length=10, choices=HeightRange.choices
    )
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='products/images', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.product_name
