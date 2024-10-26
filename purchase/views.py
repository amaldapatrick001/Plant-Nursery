from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views import View
from purchase.forms import CheckoutForm
from userauths.models import User_Reg
from products.models import Batch
from .models import  Billing, Cart, CartItem, Order  # Only import from purchase.models

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
        return redirect('products:cproduct_list')

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






from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.urls import reverse
from django.http import JsonResponse
from django.conf import settings
import razorpay
from .models import Cart, CartItem, Billing, User_Reg, Order
from .forms import CheckoutForm

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Checkout View
class CheckoutView(View):
    def get(self, request):
        # Check if the user is logged in
        if 'user_id' not in request.session:
            messages.error(request, 'You must be logged in to proceed to checkout.')
            return redirect('userauths:login')

        user_id = request.session['user_id']
        user = get_object_or_404(User_Reg, uid=user_id)

        # Fetch saved billing addresses for the user
        addresses = Billing.objects.filter(user=user)

        # Initialize the checkout form
        form = CheckoutForm()

        # Retrieve the user's cart
        cart = Cart.objects.filter(user_id=user_id).first()
        cart_items = cart.items.all() if cart else []

        # Check if cart is empty
        if not cart_items:
            messages.info(request, 'Your cart is empty.')
            return redirect('products:cproduct_list')

        # Calculate subtotal, discount, and delivery
        actual_subtotal = sum(item.get_total_price() for item in cart_items)
        total_discount = sum(item.get_discount_amount() for item in cart_items)
        delivery_price = 50  # Set delivery price here

        # Calculate total prices
        total_after_discount = actual_subtotal - total_discount
        total_price_with_delivery_and_discount = total_after_discount + delivery_price
        total_price_with_delivery_and_discounts = int((total_after_discount + delivery_price) * 100)  # Convert to paise

        # Pass all data to template
        return render(request, 'purchase/checkout.html', {
            'form': form,
            'addresses': addresses,
            'cart_items': cart_items,
            'actual_subtotal': actual_subtotal,
            'total_discount': total_discount,
            'delivery_price': delivery_price,
            'total_price_with_delivery_and_discount': total_price_with_delivery_and_discount,
            'total_after_discount': total_after_discount,
            'total_price_with_delivery_and_discounts': total_price_with_delivery_and_discounts,
        })

    def post(self, request):
        # Check if the user is logged in
        if 'user_id' not in request.session:
            messages.error(request, 'You must be logged in to proceed to checkout.')
            return redirect('userauths:login')

        user_id = request.session['user_id']
        user = get_object_or_404(User_Reg, uid=user_id)

        # Check if a saved billing address is selected
        billing_address_id = request.POST.get('selected_address')
        if billing_address_id:
            billing_address = get_object_or_404(Billing, id=billing_address_id)
        else:
            # Process form submission if no address is selected
            form = CheckoutForm(request.POST)
            if form.is_valid():
                billing_address = form.save(commit=False)
                billing_address.user = user
                billing_address.save()
            else:
                # Re-render checkout with form errors
                return self.get(request)

        # Retrieve the user's cart
        cart = Cart.objects.filter(user_id=user_id).first()
        if not cart or not cart.items.exists():
            messages.error(request, 'Your cart is empty. Please add items to your cart before proceeding.')
            return redirect('products:cproduct_list')

        # Create the order and save the billing address
        total_amount = sum(item.get_total_price_with_discount() for item in cart.items.all()) + 50  # Add delivery charge

        # Create the order and save the billing address
        order = Order.objects.create(user=user, billing=billing_address, cart=cart, total_amount=total_amount)
        messages.success(request, 'Order placed successfully!')
        return redirect(reverse('purchase:checkout'))


# Payment Gateway View
class PaymentGatewayView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        razorpay_order = razorpay_client.order.create({
            "amount": int(order.total_amount * 100),  # Amount in paisa
            "currency": "INR",
            "payment_capture": "1"
        })
        order.razorpay_order_id = razorpay_order['id']
        order.save()

        context = {
            "order": order,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": razorpay_order['id'],
            "amount": order.total_amount,
            "currency": "INR"
        }
        return render(request, "purchase/checkout.html", context)

# from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from .models import Order

def payment_success(request):
    # Check if the user is logged in using session
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to complete the payment.')
        return redirect('userauths:login')

    if request.method == "POST":
        data = request.POST
        razorpay_payment_id = data['razorpay_payment_id']
        razorpay_order_id = data['razorpay_order_id']
        
        # Get the order associated with the Razorpay order ID
        order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)
        
        # Update payment and order status
        order.mark_payment_successful(razorpay_payment_id)
        order.status = "Completed"
        order.cart.is_completed = True  # Update the cart status
        order.cart.save()  # Save the cart changes
        order.save()

        return JsonResponse({"message": "Payment successful."})

# Payment Failure View
def payment_failure(request):
    return JsonResponse({"message": "Payment failed. Please try again."})





# Order Summary View
class OrderSummaryView(View):
    def get(self, request, order_id):
        # Display the order summary page
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'purchase/order_summary.html', {'order': order})

# Order Confirmation View
class OrderConfirmationView(View):
    def get(self, request, order_id):
        # Display order confirmation
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'purchase/order_confirmation.html', {'order': order})
from django.shortcuts import render, redirect







from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Billing

def delete_address_view(request, id):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to delete an address.')
        return redirect('userauths:login')

    address = get_object_or_404(Billing, id=id)

    # Optional: Check if the address belongs to the logged-in user
    if address.user.uid != request.session['user_id']:
        messages.error(request, 'You do not have permission to delete this address.')
        return redirect('purchase:checkout')

    address.delete()
    messages.success(request, 'Address deleted successfully.')
    return redirect('purchase:checkout')  # Redirect back to the checkout page














from django.shortcuts import render, redirect

def set_delivery_address(request):
    if request.method == 'POST':
        # Logic to save or set the delivery address
        pass
    return redirect('purchase:checkout')
