from django.db import models
from django.conf import settings
from userauths.models import Login
from products.models import Batch, Product

class Cart(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.email}"

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
        # Assuming discount is a percentage, adjust if it's a flat amount.
        discount = self.batch.discount if hasattr(self.batch, 'discount') else 0
        return (self.get_total_price() * discount) / 100

    def get_total_price_with_discount(self):
        return self.get_total_price() - self.get_discount_amount()

    def get_discount(self):
        return self.batch.discount_amount if hasattr(self.batch, 'discount_amount') else 0



from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count

# Permanent delivery charges based on districts
DELIVERY_CHARGES = {
    'kottayam': 50.00,
    'idukki': 70.00,
    'alappuzha': 60.00,
    'pathanamthitta': 80.00,
}

class Billing(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    district = models.CharField(max_length=50)
    street_address = models.CharField(max_length=255)
    town_city = models.CharField(max_length=50)
    postcode_zip = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.district}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)  # Linking to cart
    payment_method = models.CharField(max_length=20)  # e.g., Direct Bank Transfer, PayPal
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)

    # New fields for order tracking
    first_order_date = models.DateTimeField(null=True, blank=True)
    last_order_date = models.DateTimeField(null=True, blank=True)
    total_orders = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk:  # If the order is being created (not updated)
            self.update_order_stats()
        super().save(*args, **kwargs)

    def update_order_stats(self):
        # Get all orders for the user
        orders = Order.objects.filter(user=self.user)
        
        if orders.exists():
            self.first_order_date = orders.order_by('order_date').first().order_date
            self.last_order_date = self.order_date
            self.total_orders = orders.count() + 1  # +1 for the current order
        else:
            self.first_order_date = self.order_date
            self.last_order_date = self.order_date
            self.total_orders = 1  # First order

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
