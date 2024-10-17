from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views import View
from .forms import CheckoutForm
from products.models import Batch
from .models import  Billing, Cart, CartItem, Order, OrderItem  # Only import from purchase.models

# Add item to cart view
def add_to_cart(request, batch_id):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to your cart.')
        return redirect('userauths:login')

    batch = get_object_or_404(Batch, id=batch_id)

    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user_id=request.session['user_id'])

    # Check if the item is already in the cart
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, batch=batch)

    # If the item is already in the cart, update the quantity
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"{batch.product.name} quantity updated in your cart.")
    else:
        messages.success(request, f"{batch.product.name} added to your cart.")

    return redirect('purchase:cart_detail')
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cart, CartItem

def cart_detail(request):
    # Fetch the cart for the current user
    cart = Cart.objects.filter(user_id=request.session['user_id']).first()
    
    if not cart or not cart.items.exists():
        messages.info(request, 'Your cart is empty.')
        return redirect('products:product_list')

    # Calculate subtotal, total discount, and delivery price
    actual_subtotal = sum(item.get_total_price() for item in cart.items.all())
    total_discount = sum(item.get_discount_amount() for item in cart.items.all())  # Use get_discount_amount here
    delivery_price = 50  # Set your delivery price logic here

    # Calculate the total price with discount and delivery
    total_price_with_delivery_and_discount = (actual_subtotal - total_discount) + delivery_price
    total_after_discount = actual_subtotal - total_discount
    context = {
        'cart_items': cart.items.all(),
        'actual_subtotal': actual_subtotal,
        'total_discount': total_discount,
        'delivery_price': delivery_price,
        'total_price_with_delivery_and_discount': total_price_with_delivery_and_discount,
        'total_after_discount': total_after_discount, 
    }

    return render(request, 'purchase/cart_detail.html', context)





# Remove item from cart view
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    # Ensure the item belongs to the current user
    if cart_item.cart.user_id != request.session.get('user_id'):
        messages.error(request, 'You are not authorized to remove this item.')
        return redirect('purchase:cart_detail')

    cart_item.delete()
    messages.success(request, f'Item "{cart_item.batch.product.name}" removed from your cart.')
    return redirect('purchase:cart_detail')


# Update cart quantities view
def update_cart(request):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to update your cart.')
        return redirect('userauths:login')

    cart = Cart.objects.filter(user_id=request.session['user_id']).first()

    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('purchase:cart_detail')

    # Update quantities for each cart item
    for item in cart.items.all():
        quantity = request.POST.get(f'quantities_{item.id}')
        if quantity:
            try:
                item.quantity = int(quantity)
                if item.quantity < 1:
                    item.quantity = 1  # Prevent quantity from being less than 1
                item.save()
            except ValueError:
                messages.error(request, 'Invalid quantity entered.')
                return redirect('purchase:cart_detail')

    messages.success(request, 'Cart updated successfully.')
    return redirect('purchase:cart_detail')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views import View
from .forms import CheckoutForm
from products.models import Batch
from .models import Billing, Cart, Order  # Only import from purchase.models
from userauths.models import User_Reg  # Adjust the import based on your project structure

class CheckoutView(View):
    def get(self, request):
        # Check if the user is logged in via the session
        if 'user_id' not in request.session:
            messages.error(request, 'You must be logged in to proceed to checkout.')
            return redirect('userauths:login')

        form = CheckoutForm()
        return render(request, 'purchase/checkout.html', {'form': form})

    def post(self, request):
        # Check if the user is logged in via the session
        if 'user_id' not in request.session:
            messages.error(request, 'You must be logged in to proceed to checkout.')
            return redirect('userauths:login')

        form = CheckoutForm(request.POST)
        if form.is_valid():
            user_id = request.session['user_id']
            # Retrieve the user instance using the correct field (assuming 'uid' is the primary key)
            user = get_object_or_404(User_Reg, uid=user_id)  # Replace 'uid' with the actual primary key if different

            # Check if a billing instance already exists for this user
            billing, created = Billing.objects.get_or_create(user=user)

            # If a billing instance already exists, update it
            if not created:
                # Update existing billing information
                billing.first_name = form.cleaned_data['first_name']
                billing.last_name = form.cleaned_data['last_name']
                billing.district = form.cleaned_data['district']
                billing.street_address = form.cleaned_data['street_address']
                billing.town_city = form.cleaned_data['town_city']
                billing.postcode_zip = form.cleaned_data['postcode_zip']
                billing.phone = form.cleaned_data['phone']
                billing.email = form.cleaned_data['email']
            else:
                # Create a new billing instance
                billing.first_name = form.cleaned_data['first_name']
                billing.last_name = form.cleaned_data['last_name']
                billing.district = form.cleaned_data['district']
                billing.street_address = form.cleaned_data['street_address']
                billing.town_city = form.cleaned_data['town_city']
                billing.postcode_zip = form.cleaned_data['postcode_zip']
                billing.phone = form.cleaned_data['phone']
                billing.email = form.cleaned_data['email']

            billing.save()

            # Retrieve the user's cart
            cart = Cart.objects.filter(user_id=user_id).first()
            if not cart:
                messages.error(request, 'Your cart is empty. Please add items to your cart before proceeding.')
                return redirect('purchase:cart_detail')

            # Create the order
            order = Order.objects.create(user=user, billing=billing, cart=cart)

            messages.success(request, 'Order placed successfully!')
            return redirect(reverse('purchase:order_summary', kwargs={'order_id': order.id}))

        # If the form is not valid, render the checkout page with errors
        return render(request, 'purchase/checkout.html', {'form': form})












    
# Order Summary/Review Page View
class OrderSummaryView(View):
    def get(self, request, order_id):
        # Display the order summary page
        order = Order.objects.get(id=order_id)
        return render(request, 'purchase/order_summary.html', {'order': order})

# Order Confirmation Page View
class OrderConfirmationView(View):
    def get(self, request, order_id):
        # Display order confirmation
        order = Order.objects.get(id=order_id)
        return render(request, 'order_confirmation.html', {'order': order})

# Payment Gateway Integration (Dummy View)
class PaymentGatewayView(View):
    def get(self, request, order_id):
        order = Order.objects.get(id=order_id)
        # Payment gateway logic goes here
        # Redirect to payment confirmation page
        return redirect(reverse('order_confirmation', kwargs={'order_id': order.id}))
