# Generated by Django 5.1.2 on 2024-10-16 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0003_remove_order_delivery_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]