# Generated by Django 5.1.4 on 2025-01-02 03:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0021_delete_review'),
        ('purchase', '0009_alter_review_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='products.product'),
        ),
    ]
