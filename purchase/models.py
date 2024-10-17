from django.db import models
from userauths.models import Login,User_Reg
from products.models import Batch, Product


class Cart(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)  # New field

    def __str__(self):
        return f"Cart of {self.user.email} - Completed: {self.is_completed}"

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
        discount = self.batch.discount if hasattr(self.batch, 'discount') else 0
        return (self.get_total_price() * discount) / 100

    def get_total_price_with_discount(self):
        return self.get_total_price() - self.get_discount_amount()

    def get_discount(self):
        return self.batch.discount_amount if hasattr(self.batch, 'discount_amount') else 0

from django.db import models
from products.models import Batch

districts = {
    'kottayam': 'Kottayam',
    'pathanamthitta': 'Pathanamthitta',
    'idukki': 'Idukki',
    'thodupuzha': 'Thodupuzha',
    'ernakulam': 'Ernakulam',
}

class Billing(models.Model):
    user = models.OneToOneField(User_Reg, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    district = models.CharField(max_length=50, choices=[(key, value) for key, value in districts.items()])
    street_address = models.CharField(max_length=255)
    town_city = models.CharField(max_length=50)
    postcode_zip = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.district}"

class Order(models.Model):
    user = models.ForeignKey(User_Reg, on_delete=models.CASCADE)
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)

    def calculate_totals(self):
        cart_items = self.cart.items.all()
        subtotal = sum(item.get_total_price() for item in cart_items)
        total_discount = sum(item.get_discount_amount() for item in cart_items)
        total_price = subtotal - total_discount
        return subtotal, total_discount, total_price

    def save(self, *args, **kwargs):
        subtotal, total_discount, total_price = self.calculate_totals()
        self.subtotal = subtotal
        self.total_discount = total_discount
        self.total_price = total_price
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.batch.product.name} - Quantity: {self.quantity} - Price: {self.price}"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20)  # e.g., 'stripe', 'paypal'
    payment_status = models.CharField(max_length=20, default='Pending')  # e.g., 'Completed', 'Failed'
    transaction_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Payment {self.id} - {self.payment_status} - {self.amount}"
