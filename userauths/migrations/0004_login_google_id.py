# Generated by Django 5.1.2 on 2024-12-27 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0003_login_is_google_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='login',
            name='google_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
