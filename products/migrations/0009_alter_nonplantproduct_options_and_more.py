# Generated by Django 5.0.7 on 2024-10-11 19:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_product_plant_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='nonplantproduct',
            options={'verbose_name_plural': 'Non-Plant Products'},
        ),
        migrations.RemoveField(
            model_name='cultivationmethod',
            name='product',
        ),
        migrations.RemoveField(
            model_name='nonplantproduct',
            name='discount',
        ),
        migrations.RemoveField(
            model_name='product',
            name='best_time_to_plant',
        ),
        migrations.RemoveField(
            model_name='product',
            name='climate_suitability',
        ),
        migrations.RemoveField(
            model_name='product',
            name='growth_rate',
        ),
        migrations.RemoveField(
            model_name='product',
            name='soil_type',
        ),
        migrations.RemoveField(
            model_name='product',
            name='sunlight_requirement',
        ),
        migrations.RemoveField(
            model_name='product',
            name='water_requirement',
        ),
        migrations.AddField(
            model_name='cultivationmethod',
            name='plant_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cultivation_methods', to='products.plantcategory'),
        ),
        migrations.AddField(
            model_name='plantcategory',
            name='best_time_to_plant',
            field=models.CharField(blank=True, choices=[('spring', 'Spring'), ('summer', 'Summer'), ('autumn', 'Autumn'), ('winter', 'Winter')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='plantcategory',
            name='climate_suitability',
            field=models.CharField(blank=True, choices=[('tropical', 'Tropical (hot and humid conditions)'), ('subtropical', 'Subtropical (warm with cooler winters)'), ('temperate', 'Temperate (moderate temperatures)')], default='tropical', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='plantcategory',
            name='growth_rate',
            field=models.CharField(blank=True, choices=[('slow', 'Slow (takes longer to mature)'), ('medium', 'Medium (average growth rate)'), ('fast', 'Fast (grows quickly)')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='plantcategory',
            name='pot_soil',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='plantcategory',
            name='soil_type',
            field=models.CharField(blank=True, choices=[('loamy', 'Loamy (well-draining, nutrient-rich)'), ('sandy', 'Sandy (well-draining but nutrient-poor)'), ('clay', 'Clay (holds moisture but can be compacted)'), ('peat', 'Peat (rich in organic matter, retains moisture)'), ('silt', 'Silt (holds moisture and nutrients well)')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='plantcategory',
            name='sunlight_requirement',
            field=models.CharField(blank=True, choices=[('full_sun', 'Full Sun (6+ hours of direct sunlight)'), ('partial_sun', 'Partial Sun (4-6 hours of direct sunlight)'), ('partial_shade', 'Partial Shade (2-4 hours of direct sunlight)'), ('full_shade', 'Full Shade (less than 2 hours of direct sunlight)')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='plantcategory',
            name='water_requirement',
            field=models.CharField(blank=True, choices=[('low', 'Low (water every 1-2 weeks)'), ('medium', 'Medium (water weekly)'), ('high', 'High (water multiple times a week)')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='cultivationmethod',
            name='pit_size_width',
            field=models.DecimalField(decimal_places=2, default=1.0, help_text='Width of the pit in meters', max_digits=5),
        ),
        migrations.AlterField(
            model_name='nonplantproduct',
            name='status',
            field=models.BooleanField(default=True, help_text='Set to active or inactive.'),
        ),
        migrations.AlterField(
            model_name='plantcategory',
            name='plant_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='products.planttype'),
        ),
    ]