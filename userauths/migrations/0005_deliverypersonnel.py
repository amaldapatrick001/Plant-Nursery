# Generated by Django 5.1.4 on 2025-01-04 06:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0004_login_google_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryPersonnel',
            fields=[
                ('delivery_person_id', models.AutoField(primary_key=True, serialize=False)),
                ('current_location', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('available', 'Available'), ('busy', 'Busy')], default='available', max_length=20)),
                ('assigned_orders', models.IntegerField(default=0)),
                ('date_time_joined', models.DateTimeField(auto_now_add=True)),
                ('login', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='userauths.login')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='userauths.user_reg')),
            ],
        ),
    ]
