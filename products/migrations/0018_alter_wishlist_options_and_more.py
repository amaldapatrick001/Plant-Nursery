<<<<<<< HEAD
# Generated by Django 5.0.7 on 2024-10-13 13:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0017_wishlist'),
        ('userauths', '0002_login_login_count_user_reg_status_alter_login_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='wishlist',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='wishlist',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='wishlist',
            name='batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.batch'),
        ),
        migrations.AddField(
            model_name='wishlist',
            name='email',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='userauths.user_reg'),
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='product',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='user_email',
        ),
    ]
=======
# Generated by Django 5.0.7 on 2024-10-13 13:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0017_wishlist'),
        ('userauths', '0002_login_login_count_user_reg_status_alter_login_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='wishlist',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='wishlist',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='wishlist',
            name='batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.batch'),
        ),
        migrations.AddField(
            model_name='wishlist',
            name='email',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='userauths.user_reg'),
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='product',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='user_email',
        ),
    ]
>>>>>>> 1f7ed6f7831d74d3de04e0424065c63794fd8d85
