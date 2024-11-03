from datetime import timedelta, timezone
from django.db import models
from userauths.models import Login, User_Reg
from products.models import Batch

# Cart Model
class Cart(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Cart of {self.user.email} - Completed: {self.is_completed}"


# CartItem Model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.batch.product.name} - {self.batch.price} - Quantity: {self.quantity}"

    def get_total_price(self):
        return self.batch.price * self.quantity

    def get_discount_amount(self):
        discount = getattr(self.batch, 'discount', 0)
        return (self.get_total_price() * discount) / 100

    def get_total_price_with_discount(self):
        return self.get_total_price() - self.get_discount_amount()


# Billing Model
class Billing(models.Model):
    user = models.ForeignKey(User_Reg, on_delete=models.CASCADE)  # Changed to ForeignKey
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    district = models.CharField(max_length=50, choices=[
        ('kottayam', 'Kottayam'),
        ('pathanamthitta', 'Pathanamthitta'),
        ('idukki', 'Idukki'),
        ('thodupuzha', 'Thodupuzha'),
        ('ernakulam', 'Ernakulam'),
    ])
    street_address = models.CharField(max_length=255)
    town_city = models.CharField(max_length=50)
    postcode_zip = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.district}"


# Order Model
class Order(models.Model):
    user = models.ForeignKey(User_Reg, on_delete=models.CASCADE)
    billing = models.ForeignKey(Billing, on_delete=models.SET_NULL, null=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed')
    ]
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount for the order
  
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='Pending'
    )
    payment_date = models.DateTimeField(blank=True, null=True)

    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(blank=True, null=True)  # Set upon shipment or delivery

    def __str__(self):
        return f"Order {self.id} by {self.user.email} - Status: {self.status}"

def mark_payment_successful(self, payment_id):
    """Mark payment as successful and log the payment date."""
    self.payment_status = 'Success'
    self.razorpay_order_id = payment_id
    self.payment_date = timezone.now()
    self.save()


    def set_delivery_date(self, delivery_date=None):
        """Set delivery date; defaults to 5 days from now if not provided."""
        self.delivery_date = delivery_date or timezone.now() + timedelta(days=5)
        self.save()


