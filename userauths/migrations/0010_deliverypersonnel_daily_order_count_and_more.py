# Generated by Django 5.1.2 on 2025-02-03 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0009_deliverypersonnel_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverypersonnel',
            name='daily_order_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='deliverypersonnel',
            name='last_order_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='deliverypersonnel',
            name='max_daily_orders',
            field=models.PositiveIntegerField(default=10),
        ),
        migrations.AddField(
            model_name='deliverypersonnel',
            name='vehicle_number',
            field=models.CharField(blank=True, help_text='Enter vehicle registration number (e.g., KL-05-AB-1234)', max_length=15, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='deliverypersonnel',
            name='profile_picture',
            field=models.ImageField(blank=True, help_text='Upload a profile picture (optional)', null=True, upload_to='delivery_personnel/profiles/'),
        ),
    ]
