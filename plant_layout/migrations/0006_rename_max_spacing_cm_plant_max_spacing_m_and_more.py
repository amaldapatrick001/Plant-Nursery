# Generated by Django 5.1.2 on 2025-02-26 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plant_layout', '0005_plant_max_spacing_cm_alter_plant_min_spacing_cm_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='plant',
            old_name='max_spacing_cm',
            new_name='max_spacing_m',
        ),
        migrations.RenameField(
            model_name='plant',
            old_name='min_spacing_cm',
            new_name='min_spacing_m',
        ),
        migrations.AddField(
            model_name='userlayout',
            name='background_color',
            field=models.CharField(default='#FFFFFF', max_length=7),
        ),
        migrations.AddField(
            model_name='userlayout',
            name='background_type',
            field=models.CharField(choices=[('image', 'Image'), ('color', 'Color')], default='image', max_length=10),
        ),
    ]
