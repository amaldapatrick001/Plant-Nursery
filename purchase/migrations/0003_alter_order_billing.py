# Generated by Django 5.1.2 on 2024-10-26 07:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0002_auto_20241026_0813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='billing',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='purchase.billing'),
        ),
    ]