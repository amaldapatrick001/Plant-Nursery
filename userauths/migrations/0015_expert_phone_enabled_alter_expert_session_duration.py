# Generated by Django 5.1.2 on 2025-02-09 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0014_expert_chat_enabled_expert_meet_link_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='expert',
            name='phone_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='expert',
            name='session_duration',
            field=models.IntegerField(default=10),
        ),
    ]
