<<<<<<< HEAD
# Generated by Django 5.0.7 on 2024-09-18 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='login',
            name='login_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user_reg',
            name='status',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='login',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]
=======
# Generated by Django 5.0.7 on 2024-09-18 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='login',
            name='login_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user_reg',
            name='status',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='login',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]
>>>>>>> 1f7ed6f7831d74d3de04e0424065c63794fd8d85
