# Generated by Django 5.1.2 on 2025-02-24 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plant_layout', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlayout',
            name='plant_positions',
            field=models.JSONField(default=dict),
        ),
    ]
