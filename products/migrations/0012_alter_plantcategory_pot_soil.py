# Generated by Django 5.0.7 on 2024-10-12 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_alter_category_name_alter_planttype_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plantcategory',
            name='pot_soil',
            field=models.CharField(blank=True, choices=[('pot', 'Select Pot'), ('soil', 'Select Soil'), ('both', 'Both')], max_length=10, null=True),
        ),
    ]