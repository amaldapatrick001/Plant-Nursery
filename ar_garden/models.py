from django.db import models
from django.core.exceptions import ValidationError
from math import sqrt

from userauths.models import User_Reg

# Model to store uploaded field images
# ar_garden/models.py
from django.db import models
from django.core.exceptions import ValidationError
from math import sqrt
from userauths.models import User_Reg

class FieldImage(models.Model):
    user = models.ForeignKey(User_Reg, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='field_images/')
    width = models.FloatField(help_text="Field width in meters", default=10.0)
    length = models.FloatField(help_text="Field length in meters", default=10.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Field {self.id} - {self.user.first_name}"

    def clean(self):
        if self.width <= 0:
            raise ValidationError("Width must be greater than 0")
        if self.length <= 0:
            raise ValidationError("Length must be greater than 0")

# Model to store plant types with required spacing
class PlantType(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='plant_icons/')
    model_3d = models.FileField(upload_to='plant_models/', help_text="3D model file (.glb or .gltf)")
    min_spacing = models.FloatField(help_text="Minimum spacing between plants in meters")
    height = models.FloatField(help_text="Average height of the plant in meters")
    
    def __str__(self):
        return self.name

# Model to store user-selected plant placements
class UserPlantSelection(models.Model):
    user = models.ForeignKey(User_Reg, on_delete=models.CASCADE)  # Changed from user_id to user
    field = models.ForeignKey(FieldImage, on_delete=models.CASCADE)
    plant = models.ForeignKey(PlantType, on_delete=models.CASCADE)
    x_position = models.FloatField()
    y_position = models.FloatField()
    rotation = models.FloatField(default=0)
    is_ai_placed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        existing_plants = UserPlantSelection.objects.filter(field=self.field)
        max_spacing = max([p.plant.min_spacing for p in existing_plants], default=0)

        for existing_plant in existing_plants:
            distance = sqrt((self.x_position - existing_plant.x_position)**2 +
                            (self.y_position - existing_plant.y_position)**2)
            if distance > max_spacing:
                raise ValidationError(f"Plant is too far! Maximum allowed distance: {max_spacing}m")

        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['field', 'x_position', 'y_position'],
                name='unique_plant_position'
            )
        ]
