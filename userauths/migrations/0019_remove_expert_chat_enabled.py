# Generated by Django 5.1.7 on 2025-03-18 00:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0018_expert_chat_enabled_expert_meet_link_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expert',
            name='chat_enabled',
        ),
    ]
