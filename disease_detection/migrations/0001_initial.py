from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PlantImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='plant_images/')),
                ('disease_detected', models.CharField(blank=True, max_length=255, null=True)),
                ('confidence', models.FloatField(blank=True, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ] 