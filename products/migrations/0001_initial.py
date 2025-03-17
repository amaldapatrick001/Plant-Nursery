# Generated by Django 5.1.2 on 2025-02-06 16:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('userauths', '0013_deliverypersonnel_current_latitude_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField()),
                ('is_plant', models.BooleanField(default=False)),
                ('status', models.BooleanField(default=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlantCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('pot_soil', models.CharField(blank=True, choices=[('pot', 'Select Pot'), ('soil', 'Select Soil'), ('both', 'Both')], max_length=10, null=True)),
                ('sunlight_requirement', models.CharField(blank=True, choices=[('full_sun', 'Full Sun (6+ hours of direct sunlight)'), ('partial_sun', 'Partial Sun (4-6 hours of direct sunlight)'), ('partial_shade', 'Partial Shade (2-4 hours of direct sunlight)'), ('full_shade', 'Full Shade (less than 2 hours of direct sunlight)')], max_length=20, null=True)),
                ('water_requirement', models.CharField(blank=True, choices=[('low', 'Low (water every 1-2 weeks)'), ('medium', 'Medium (water weekly)'), ('high', 'High (water multiple times a week)')], max_length=20, null=True)),
                ('soil_type', models.CharField(blank=True, choices=[('loamy', 'Loamy (well-draining, nutrient-rich)'), ('sandy', 'Sandy (well-draining but nutrient-poor)'), ('clay', 'Clay (holds moisture but can be compacted)'), ('peat', 'Peat (rich in organic matter, retains moisture)'), ('silt', 'Silt (holds moisture and nutrients well)')], max_length=20, null=True)),
                ('growth_rate', models.CharField(blank=True, choices=[('slow', 'Slow (takes longer to mature)'), ('medium', 'Medium (average growth rate)'), ('fast', 'Fast (grows quickly)')], max_length=20, null=True)),
                ('climate_suitability', models.CharField(blank=True, choices=[('tropical', 'Tropical (hot and humid conditions)'), ('subtropical', 'Subtropical (warm with cooler winters)'), ('temperate', 'Temperate (moderate temperatures)')], max_length=20, null=True)),
                ('best_time_to_plant', models.CharField(blank=True, choices=[('spring', 'Spring'), ('summer', 'Summer'), ('autumn', 'Autumn'), ('winter', 'Winter')], max_length=20, null=True)),
                ('status', models.BooleanField(default=True, help_text='Set to active or inactive.')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Plant Categories',
            },
        ),
        migrations.CreateModel(
            name='NonPlantProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock_quantity', models.PositiveIntegerField()),
                ('is_organic', models.BooleanField(default=False)),
                ('usage', models.TextField()),
                ('suitable_for_plants', models.TextField()),
                ('image_1', models.ImageField(upload_to='non_plant_products/')),
                ('image_2', models.ImageField(blank=True, null=True, upload_to='non_plant_products/')),
                ('image_3', models.ImageField(blank=True, null=True, upload_to='non_plant_products/')),
                ('status', models.BooleanField(default=True, help_text='Set to active or inactive.')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(limit_choices_to={'is_plant': False}, on_delete=django.db.models.deletion.CASCADE, related_name='non_plant_products', to='products.category')),
            ],
            options={
                'verbose_name_plural': 'Non-Plant Products',
            },
        ),
        migrations.CreateModel(
            name='CultivationMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('desc', models.TextField()),
                ('steps', models.TextField()),
                ('recommended_tools', models.TextField(blank=True, null=True)),
                ('pit_size_height', models.DecimalField(decimal_places=2, default=1.0, help_text='Height of the pit in meters', max_digits=5)),
                ('pit_size_width', models.DecimalField(decimal_places=2, default=1.0, help_text='Width of the pit in meters', max_digits=5)),
                ('distance_between_plants', models.DecimalField(decimal_places=2, default=1.0, help_text='Distance between plants in meters', max_digits=5)),
                ('watering_frequency', models.CharField(max_length=50)),
                ('fertilization_guidelines', models.TextField(blank=True, null=True)),
                ('common_issues', models.TextField(blank=True, null=True)),
                ('status', models.BooleanField(default=True, help_text='Set to active or inactive.')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('plant_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cultivation_methods', to='products.plantcategory')),
            ],
            options={
                'verbose_name_plural': 'Cultivation Methods',
            },
        ),
        migrations.CreateModel(
            name='PlantType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField()),
                ('status', models.BooleanField(default=True, help_text='Set to active or inactive.')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(limit_choices_to={'is_plant': True}, on_delete=django.db.models.deletion.CASCADE, to='products.category')),
            ],
            options={
                'verbose_name_plural': 'Plant Types',
            },
        ),
        migrations.AddField(
            model_name='plantcategory',
            name='plant_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='products.planttype'),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('image_1', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('image_2', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('image_3', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('status', models.BooleanField(default=True, help_text='Set to active or inactive.')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('plant_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.plantcategory')),
                ('plant_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.planttype')),
            ],
            options={
                'verbose_name_plural': 'Products',
            },
        ),
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_height', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock_quantity', models.PositiveIntegerField()),
                ('no_of_plants', models.PositiveIntegerField(default=1)),
                ('discount', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('short_description', models.TextField(blank=True, null=True)),
                ('status', models.BooleanField(default=True, help_text='Set to active or inactive.')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='batches', to='products.product')),
            ],
            options={
                'verbose_name_plural': 'Batches',
            },
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('batch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.batch')),
                ('email', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='userauths.login')),
            ],
        ),
    ]
