# Generated by Django 5.1.2 on 2024-11-03 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0002_login_login_count_user_reg_status_alter_login_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='login',
            name='is_google_user',
            field=models.BooleanField(default=False),
        ),
    ]
