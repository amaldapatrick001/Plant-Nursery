<<<<<<< HEAD
# Generated by Django 5.0.7 on 2024-10-11 07:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_planttype_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
        migrations.AddField(
            model_name='product',
            name='Plant_Type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.planttype'),
        ),
    ]
=======
# Generated by Django 5.0.7 on 2024-10-11 07:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_planttype_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
        migrations.AddField(
            model_name='product',
            name='Plant_Type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.planttype'),
        ),
    ]
>>>>>>> 1f7ed6f7831d74d3de04e0424065c63794fd8d85
