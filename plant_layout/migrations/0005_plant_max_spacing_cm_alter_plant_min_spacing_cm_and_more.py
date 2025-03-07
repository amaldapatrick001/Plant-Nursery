# Generated by Django 5.1.2 on 2025-02-25 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plant_layout', '0004_alter_userlayout_options_userlayout_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='plant',
            name='max_spacing_cm',
            field=models.FloatField(default=1.0, help_text='Maximum spacing between plants in centimeters'),
        ),
        migrations.AlterField(
            model_name='plant',
            name='min_spacing_cm',
            field=models.FloatField(default=1.0, help_text='Minimum spacing between plants in centimeters'),
        ),
        migrations.AlterField(
            model_name='plant',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='userlayout',
            name='plot_image',
            field=models.ImageField(blank=True, null=True, upload_to='plots/'),
        ),
    ]
