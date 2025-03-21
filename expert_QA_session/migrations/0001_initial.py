# Generated by Django 5.1.7 on 2025-03-17 16:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('userauths', '0018_expert_chat_enabled_expert_meet_link_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to='userauths.user_reg')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userauths.user_reg')),
            ],
        ),
        migrations.CreateModel(
            name='ExpertSession',
            fields=[
                ('session_id', models.AutoField(primary_key=True, serialize=False)),
                ('session_type', models.CharField(choices=[('chat', 'Chat Session'), ('phone', 'Phone Call'), ('video', 'Video Call')], max_length=10)),
                ('session_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expert', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userauths.expert')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userauths.user_reg')),
            ],
            options={
                'ordering': ['-session_date'],
            },
        ),
    ]
