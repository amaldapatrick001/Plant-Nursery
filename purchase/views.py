from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cart, CartItem  # Only import from purchase.models
from products.models import Batch  # Keep Batch import from products

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
    total_discount = sum(item.get_discount() for item in cart.items.all())
    delivery_price = 10  # Set your delivery price logic here

    # Calculate the total price with discount and delivery
    total_price_with_delivery_and_discount = (actual_subtotal - total_discount) + delivery_price

    context = {
        'cart_items': cart.items.all(),
        'actual_subtotal': actual_subtotal,
        'total_discount': total_discount,
        'delivery_price': delivery_price,
        'total_price_with_delivery_and_discount': total_price_with_delivery_and_discount,
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

from django.shortcuts import render, redirect
from django.contrib import messages

def checkout(request):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to proceed with checkout.')
        return redirect('userauths:login')

    cart = Cart.objects.filter(user_id=request.session['user_id']).first()

    if not cart or not cart.items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('purchase:cart_detail')

    # Logic for handling the checkout process (e.g., calculating total, saving order, etc.)
    total_price = sum(item.get_total_price() for item in cart.items.all())

    context = {
        'cart_items': cart.items.all(),
        'total_price': total_price,
    }

    return render(request, 'purchase/checkout.html', context)



def place_order(request):
    # Logic for placing the order
    # Save order details, charge payment, etc.
    # Clear the cart after successful order placement
    
    messages.success(request, 'Your order has been placed successfully.')
    return redirect('purchase:order_confirmation')
