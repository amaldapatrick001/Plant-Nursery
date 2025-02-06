from datetime import timezone
from django.db import models
from userauths.models import Login, User_Reg, DeliveryPersonnel
from products.models import Batch, Product
from django.core.mail import send_mail

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
        # Use a default discount of 0 if it's None
        discount = self.batch.discount if self.batch.discount is not None else 0
        return (self.get_total_price() * discount) / 100


    def get_total_price_with_discount(self):
        return self.get_total_price() - self.get_discount_amount()


# Billing Modelclass 
class Billing(models.Model):
    user = models.ForeignKey(User_Reg, on_delete=models.CASCADE)
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

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancel', 'Cancel'),
        ('return', 'Return'),
    ]

    user = models.ForeignKey(User_Reg, on_delete=models.CASCADE)
    billing = models.ForeignKey(Billing, on_delete=models.SET_NULL, null=True)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed')
    ]
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending') 
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    assigned_delivery_person = models.ForeignKey(DeliveryPersonnel, null=True, blank=True, on_delete=models.SET_NULL)
    delivery_location = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.first_name}"

    def assign_delivery_personnel(self):
        delivery_personnel = DeliveryPersonnel.objects.filter(
            area_of_delivery=self.billing.district, 
            status='available',
            daily_order_count__lt=10
        ).order_by('daily_order_count').first()

        if delivery_personnel:
            self.assigned_delivery_person = delivery_personnel
            delivery_personnel.daily_order_count += 1
            delivery_personnel.status = 'busy' if delivery_personnel.daily_order_count >= 10 else 'available'
            delivery_personnel.save()
        else:
            self.delivery_date += timedelta(days=1)  # Postpone to next day if no available personnel
        
        # Adjust for Sunday holiday
        if self.delivery_date.weekday() == 6:
            self.delivery_date += timedelta(days=1)
        self.save()

    def __str__(self):
        return f"Order {self.id}"

    def __str__(self):
        return f"Order {self.id} by {self.user.email} - Status: {self.status}"

    def mark_payment_successful(self, payment_id):
        """Mark payment as successful, store order items, and clear the cart."""
        self.payment_status = 'Success'
        self.razorpay_order_id = payment_id
        self.payment_date = timezone.now()
        self.save()

        # Copy each item from CartItem to OrderItem and reduce stock accordingly
        for cart_item in self.cart.items.all():
            if cart_item.batch.stock_quantity < cart_item.quantity:
                raise ValueError(f"Insufficient stock for {cart_item.batch.product.name}. Only {cart_item.batch.stock_quantity} available.")

            # Update stock quantity
            cart_item.batch.stock_quantity -= cart_item.quantity
            cart_item.batch.save()

            OrderItem.objects.create(
                order=self,
                product=cart_item.batch.product.name,
                batch=cart_item.batch,
                quantity=cart_item.quantity,
                price=cart_item.batch.price,
                discount=getattr(cart_item.batch, 'discount', 0)
            )

        # Mark the cart as completed
        self.cart.is_completed = True
        self.cart.save()


# OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.CharField(max_length=255)  # Store product name for reference
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True)  # Link to the specific batch
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Store price at the time of order
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, null=True, blank=True)

    def __str__(self):
        return f"{self.product} - Quantity: {self.quantity} - Price: {self.price}"

    def get_total_price(self):
        return self.price * self.quantity

    def get_total_price_with_discount(self):
        return self.get_total_price() - ((self.get_total_price() * self.discount) / 100)







class Review(models.Model):
    user = models.ForeignKey(User_Reg, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, f"{i} Stars") for i in range(1, 6)])  # 1 to 5 stars
    comment = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(auto_now_add=True)
    reply = models.TextField(blank=True, null=True)  # Add reply field

    def __str__(self):
        return f"Review by {self.user.fname} for {self.product.name} - Rating: {self.rating} Stars"
