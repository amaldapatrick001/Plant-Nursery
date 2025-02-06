# Generated by Django 5.1 on 2024-10-07 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter your name', max_length=100)),
                ('email', models.EmailField(help_text='Enter your email', max_length=100)),
                ('subject', models.CharField(help_text='Enter the subject', max_length=100)),
                ('message', models.TextField(help_text='Enter your message')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
