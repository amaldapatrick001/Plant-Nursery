# Generated by Django 5.1.2 on 2024-10-26 02:43

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, to='userauths.login')),
            ],
        ),
    ]