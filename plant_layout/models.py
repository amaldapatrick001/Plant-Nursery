from django.db import models
from django.utils import timezone
from userauths.models import User_Reg



class Plant(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='plant_icons/')
    min_spacing_m = models.FloatField(help_text="Minimum spacing between plants in meters", default=1.0)
    max_spacing_m = models.FloatField(help_text="Maximum spacing between plants in meters", default=1.0)

    def __str__(self):
        return self.name


from django.core.validators import RegexValidator

class UserLayout(models.Model):
    user = models.ForeignKey(User_Reg, on_delete=models.CASCADE)
    layout_name = models.CharField(max_length=200)
    plot_image = models.ImageField(upload_to='plots/', blank=True, null=True)
    plot_width = models.FloatField(help_text="Width in meters", default=10.0)
    plot_length = models.FloatField(help_text="Length in meters", default=10.0)
    plant_positions = models.JSONField(default=dict)

    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    background_type = models.CharField(
        max_length=10, 
        choices=[('image', 'Image'), ('color', 'Color')],
        default='image'
    )
    background_color = models.CharField(
        max_length=7, 
        default='#FFFFFF',
        validators=[RegexValidator(regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', message='Enter a valid hex color code.')]
    )

    def __str__(self):
        return f"{self.user.username}'s layout: {self.layout_name}"

    class Meta:
        ordering = ['-updated_at']

    def save(self, *args, **kwargs):
        if not self.plant_positions:
            self.plant_positions = {'dimensions': {'width': self.plot_width, 'length': self.plot_length}, 'plants': []}
        super().save(*args, **kwargs)