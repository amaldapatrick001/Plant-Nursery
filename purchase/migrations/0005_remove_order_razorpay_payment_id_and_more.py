# Generated by Django 5.1.2 on 2024-10-27 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0004_order_razorpay_payment_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='razorpay_payment_id',
        ),
        migrations.AlterField(
            model_name='order',
            name='razorpay_order_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Returned', 'Returned')], default='Pending', max_length=20),
        ),
    ]