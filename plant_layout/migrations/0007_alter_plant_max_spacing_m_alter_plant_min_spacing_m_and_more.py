# Generated by Django 5.1.2 on 2025-02-26 06:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plant_layout', '0006_rename_max_spacing_cm_plant_max_spacing_m_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plant',
            name='max_spacing_m',
            field=models.FloatField(default=1.0, help_text='Maximum spacing between plants in meters'),
        ),
        migrations.AlterField(
            model_name='plant',
            name='min_spacing_m',
            field=models.FloatField(default=1.0, help_text='Minimum spacing between plants in meters'),
        ),
        migrations.AlterField(
            model_name='userlayout',
            name='background_color',
            field=models.CharField(default='#FFFFFF', max_length=7, validators=[django.core.validators.RegexValidator(message='Enter a valid hex color code.', regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')]),
        ),
    ]
