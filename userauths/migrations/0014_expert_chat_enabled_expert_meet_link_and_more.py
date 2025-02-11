# Generated by Django 5.1.2 on 2025-02-09 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0013_deliverypersonnel_current_latitude_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='expert',
            name='chat_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='expert',
            name='meet_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='expert',
            name='session_duration',
            field=models.IntegerField(default=30),
        ),
        migrations.AddField(
            model_name='expert',
            name='session_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
