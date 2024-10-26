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
    user = models.OneToOneField(User_Reg, on_delete=models.CASCADE)
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
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount for the order
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)  # For Razorpay integration
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.email} - Status: {self.status}"


# OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.batch.product.name} - Quantity: {self.quantity} - Price: {self.price}"


from django.db import models
from django.utils import timezone

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100, null=True)  # Allow null for existing rows
    status = models.CharField(max_length=20, default='Pending')  # Status can be 'Success', 'Failed', etc.
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount paid
    created_at = models.DateTimeField(default=timezone.now)  # Use timezone.now to set default value

    def __str__(self):
        return f"Payment {self.payment_id} for Order {self.order.id}"
