from datetime import timedelta
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views import View
from purchase.forms import CheckoutForm
from userauths.models import Login, DeliveryPersonnel
from products.models import Batch
from .models import Billing, Cart, CartItem, Order, OrderItem
from .utils import calculate_cart_total  # Assuming you have this utility function
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q
from django.db.models import Sum, Count
from django.utils.dateparse import parse_date
from django.db import transaction
import logging
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.units import inch
from io import BytesIO
import qrcode
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def ensure_user_logged_in(request):
    """Ensure the user is logged in; if not, redirect to login with an error message."""
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to proceed.')
        return False
    return True

# Add item to cart view
def add_to_cart(request, batch_id):
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    batch = get_object_or_404(Batch, id=batch_id)

    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user_id=request.session['user_id'], is_completed=False)

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

def cart_detail(request):
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    # Fetch the incomplete cart for the current user
    cart = Cart.objects.filter(user_id=request.session.get('user_id'), is_completed=False).first()

    if not cart or not cart.items.exists():
        messages.info(request, 'Your cart is empty.')
        return redirect('products:cproduct_list')

    # Calculate subtotal, total discount, and delivery price
    actual_subtotal = sum(item.get_total_price() for item in cart.items.all())
    total_discount = sum(item.get_discount_amount() for item in cart.items.all())
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
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    # Ensure the item belongs to the current user
    if cart_item.cart.user_id != request.session.get('user_id'):
        messages.error(request, 'You are not authorized to remove this item.')
        return redirect('purchase:cart_detail')

    cart_item.delete()
    messages.success(request, f'Item "{cart_item.batch.product.name}" removed from your cart.')
    return redirect('purchase:cart_detail')
from django.contrib import messages

def update_cart(request):
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    cart = Cart.objects.filter(user_id=request.session.get('user_id'), is_completed=False).first()

    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('purchase:cart_detail')

    # Update quantities for each cart item
    for item in cart.items.all():
        quantity = request.POST.get(f'quantities_{item.id}')
        if quantity:
            try:
                quantity = int(quantity)
                # Ensure at least 1 quantity
                if quantity < 1:
                    quantity = 1

                # Check if requested quantity is available in stock (using Batch's stock_quantity field)
                available_stock = item.batch.stock_quantity  # Using stock_quantity from the Batch model
                if quantity > available_stock:
                    messages.error(request, f'Not enough stock for {item.batch.product.name}. Available stock: {available_stock}.')
                    return redirect('purchase:cart_detail')

                # Update the quantity and save the item
                item.quantity = quantity
                item.save()
            except ValueError:
                messages.error(request, 'Invalid quantity entered.')
                return redirect('purchase:cart_detail')

    messages.success(request, 'Cart updated successfully.')
    return redirect('purchase:cart_detail')




class CheckoutView(View):
    def get(self, request):
        if not ensure_user_logged_in(request):
            return redirect('userauths:login')

        try:
            user_id = request.session['user_id']
            user = Login.objects.get(login_id=user_id)
            addresses = Billing.objects.filter(user_id=user.uid_id)
            form = CheckoutForm()
            cart = Cart.objects.filter(user_id=user_id, is_completed=False).first()

            if not cart or not cart.items.exists():
                messages.info(request, 'Your cart is empty.')
                return redirect('products:cproduct_list')

            # Calculate totals
            cart_items = cart.items.all()
            actual_subtotal = sum(item.get_total_price() for item in cart_items)
            total_discount = sum(item.get_discount_amount() for item in cart_items)
            delivery_price = 50  # Fixed delivery price

            # Calculate final totals
            total_after_discount = actual_subtotal - total_discount
            total_price_with_delivery_and_discount = total_after_discount + delivery_price
            total_price_with_delivery_and_discounts = int(total_price_with_delivery_and_discount * 100)  # Amount in paise for Razorpay

            # Get selected address from session
            selected_address_id = request.session.get('selected_address_id')

            # Create or get existing order
            order = Order.objects.filter(
                user_id=user.uid_id,
                cart=cart,
                payment_status='Pending'
            ).first()

            if not order:
                # Create new order if none exists
                order = Order.objects.create(
                    user_id=user.uid_id,
                    cart=cart,
                    total_amount=total_price_with_delivery_and_discount,
                    payment_status='Pending'
                )
            
            request.session['current_order_id'] = order.id

            context = {
                'form': form,
                'addresses': addresses,
                'cart_items': cart_items,
                'actual_subtotal': actual_subtotal,
                'total_discount': total_discount,
                'delivery_price': delivery_price,
                'total_price_with_delivery_and_discount': total_price_with_delivery_and_discount,
                'total_price_with_delivery_and_discounts': total_price_with_delivery_and_discounts,
                'total_after_discount': total_after_discount,
                'selected_address_id': selected_address_id,
                'order': order,
                'csrf_token': request.COOKIES.get('csrftoken'),
            }

            return render(request, 'purchase/checkout.html', context)

        except Exception as e:
            logger.error(f"Error in checkout view: {str(e)}", exc_info=True)
            messages.error(request, 'An error occurred during checkout. Please try again.')
            return redirect('purchase:cart_detail')


from django.db.models import Q

@require_POST
def set_delivery_address(request):
    if not ensure_user_logged_in(request):
        return JsonResponse({'success': False, 'redirect': reverse('userauths:login')})

    try:
        user_id = request.session['user_id']
        user = Login.objects.get(login_id=user_id)

        # Handle new address form submission
        if request.POST.get('first_name'):
            form = CheckoutForm(request.POST)
            if form.is_valid():
                billing_address = form.save(commit=False)
                billing_address.user_id = user.uid_id
                billing_address.save()
                request.session['selected_address_id'] = billing_address.id
                return redirect('purchase:checkout')
            else:
                return JsonResponse({'success': False, 'error': 'Invalid form data'})

        # Handle address selection
        address_id = request.POST.get('selected_address')
        if not address_id:
            return JsonResponse({'success': False, 'error': 'No address selected'})

        billing_address = get_object_or_404(Billing, id=address_id, user_id=user.uid_id)
        
        # Update or create order with selected address
        order = Order.objects.filter(
            user_id=user.uid_id,
            payment_status='Pending'
        ).first()

        if order:
            order.billing = billing_address
            order.save()

        request.session['selected_address_id'] = billing_address.id
        
        return JsonResponse({
            'success': True,
            'address_id': billing_address.id,
            'message': 'Address selected successfully'
        })

    except Exception as e:
        logger.error(f"Error setting delivery address: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'An error occurred'})

@require_POST
def delete_address(request, address_id):
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    try:
        user_id = request.session['user_id']
        user = Login.objects.get(login_id=user_id)
        address = get_object_or_404(Billing, id=address_id, user_id=user.uid_id)
        
        # Clear session if deleted address was selected
        if str(address_id) == str(request.session.get('selected_address_id')):
            request.session['selected_address_id'] = None
            
        address.delete()
        messages.success(request, "Address deleted successfully.")
        
    except Exception as e:
        logger.error(f"Error deleting address: {str(e)}", exc_info=True)
        messages.error(request, "Failed to delete address.")
        
    return redirect('purchase:checkout')

import logging

# Create a logger for this module

logger = logging.getLogger(__name__)

def get_next_available_date(date):
    """Find the next available delivery date, avoiding Sundays."""
    while date.weekday() == 6:  # Sunday
        date += timedelta(days=1)
    return date

def assign_delivery_person(order):
    """
    Assigns a delivery person to an order and sets appropriate dates.
    Returns True if assignment successful, False if postponed.
    """
    try:
        # Find available delivery personnel in the order's district
        delivery_personnel = DeliveryPersonnel.objects.filter(
            area_of_delivery=order.billing.district,
            status='available',
            daily_order_count__lt=10
        ).order_by('daily_order_count').first()

        # Set initial delivery date (3 days from now)
        delivery_date = timezone.now() + timedelta(days=3)
        while delivery_date.weekday() == 6:  # Skip Sundays
            delivery_date += timedelta(days=1)

        if delivery_personnel:
            # Assign delivery person and update their status
            order.assigned_delivery_person = delivery_personnel
            order.status = 'assigned'
            order.delivery_date = delivery_date
            
            # Update delivery personnel details
            delivery_personnel.daily_order_count += 1
            delivery_personnel.status = 'busy' if delivery_personnel.daily_order_count >= 10 else 'available'
            delivery_personnel.last_order_date = timezone.now().date()
            
            # Save changes
            with transaction.atomic():
                delivery_personnel.save()
                order.save()
            
            return True
        else:
            # No available delivery person - still assign the next available one
            next_available = DeliveryPersonnel.objects.filter(
                area_of_delivery=order.billing.district
            ).order_by('daily_order_count').first()
            
            if next_available:
                # Assign delivery person but with a later date
                order.assigned_delivery_person = next_available
                order.status = 'assigned'
                order.delivery_date = delivery_date + timedelta(days=1)
                
                # Update delivery personnel details
                next_available.daily_order_count += 1
                next_available.last_order_date = timezone.now().date()
                
                # Save changes
                with transaction.atomic():
                    next_available.save()
                    order.save()
                
                return True
            
        return False
        
    except Exception as e:
        logger.error(f"Error assigning delivery person: {str(e)}", exc_info=True)
        return False

@require_POST
@csrf_exempt
def razorpay_checkout(request):
    try:
        # Validate request and user
        if not request.body:
            return JsonResponse({'success': False, 'error': 'No data received'}, status=400)
        
        if 'user_id' not in request.session:
            return JsonResponse({'success': False, 'error': 'User not logged in'}, status=403)

        # Parse request data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)

        user_id = request.session['user_id']
        razorpay_payment_id = data.get('razorpay_payment_id')
        order_id = request.session.get('current_order_id')

        # Validate payment and order data
        if not razorpay_payment_id:
            return JsonResponse({'success': False, 'error': 'Payment ID is required'}, status=400)
        
        if not order_id:
            return JsonResponse({'success': False, 'error': 'No active order found'}, status=400)

        # Get order and validate ownership
        try:
            order = Order.objects.get(id=order_id, user_id=user_id)
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)

        # Process payment and update order
        try:
            with transaction.atomic():
                # Update order payment details
                order.razorpay_order_id = razorpay_payment_id
                order.payment_status = "Success"
                order.payment_date = timezone.now()

                # Assign delivery person
                assignment_success = assign_delivery_person(order)
                
                if not assignment_success:
                    # If no delivery person could be assigned, set to pending
                    order.status = 'pending'
                    next_day = timezone.now() + timedelta(days=4)
                    while next_day.weekday() == 6:
                        next_day += timedelta(days=1)
                    order.delivery_date = next_day

                order.save()

                # Process cart items
                cart = Cart.objects.get(id=order.cart.id, user_id=user_id)
                
                for item in cart.items.all():
                    batch = item.batch
                    if batch.stock_quantity < item.quantity:
                        raise ValueError(f"Insufficient stock for {batch.product.name}")
                    
                    # Update stock
                    batch.stock_quantity -= item.quantity
                    batch.status = batch.stock_quantity > 0
                    batch.save()

                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product=item.batch.product.name,
                        batch=item.batch,
                        quantity=item.quantity,
                        price=item.batch.price,
                        discount=item.batch.discount or 0.0
                    )

                # Clear cart
                cart.items.all().delete()
                cart.is_completed = True
                cart.save()

            # Clear session data
            request.session['current_order_id'] = None
            
            # Generate QR code
            qr_path = generate_qr(order.id)

            # Prepare email content
            delivery_person_name = None
            vehicle_id = None
            if order.status == 'assigned' and order.assigned_delivery_person:
                delivery_person_name = f"{order.assigned_delivery_person.user.first_name} {order.assigned_delivery_person.user.last_name}"
                vehicle_id = order.assigned_delivery_person.vehicle_number

            subject = "Order Confirmation and QR Code"
            message = render_to_string('emails/order_confirmation.html', {
                'customer_name': f"{order.billing.first_name} {order.billing.last_name}",
                'order_id': order.id,
                'delivery_date': order.delivery_date.strftime('%B %d, %Y'),
                'delivery_person_name': delivery_person_name,
                'vehicle_id': vehicle_id,
            })

            # Send email with QR code
            email = EmailMessage(
                subject,
                message,
                'no-reply@yourstore.com',
                [order.billing.email]
            )
            email.attach_file(qr_path)
            email.send()

            # Prepare response message
            message = "Payment processed successfully. "
            if order.status == 'assigned' and order.assigned_delivery_person:
                message += f"Delivery assigned to {delivery_person_name} for {order.delivery_date.strftime('%B %d, %Y')}"
            else:
                message += f"Delivery scheduled for {order.delivery_date.strftime('%B %d, %Y')}"

            return JsonResponse({
                'success': True, 
                'order_id': order.id,
                'message': message,
                'status': order.status,
                'delivery_date': order.delivery_date.strftime('%B %d, %Y'),
                'delivery_person': delivery_person_name
            })

        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Transaction failed. Please try again.'
            }, status=500)

    except Exception as e:
        logger.error(f"Payment processing error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred'
        }, status=500)
    



from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, Billing

def order_summary(request, order_id):
    # Ensure user is logged in
    if not request.session.get('user_id'):
        return redirect('userauths:login')

    # Retrieve user and order details
    user_id = request.session.get('user_id')
    order = get_object_or_404(Order, id=order_id, user_id=user_id)
    order_items = order.order_items.all()

    # Calculate order summary details
    actual_subtotal = sum(item.get_total_price() for item in order_items)
    total_discount = sum((item.get_total_price() * item.discount / 100) for item in order_items)
    delivery_price = 50  # Flat rate for delivery
    total_price_with_delivery_and_discount = actual_subtotal - total_discount + delivery_price

    # Prepare context for rendering template
    qr_code_url = generate_qr(order_id)  # Ensure this returns the correct URL
    context = {
        'order': order,
        'order_items': order_items,
        'actual_subtotal': actual_subtotal,
        'total_discount': total_discount,
        'delivery_price': delivery_price,
        'total_price_with_delivery_and_discount': total_price_with_delivery_and_discount,
        'selected_address_id': request.session.get('selected_address_id'),
        'user_addresses': Billing.objects.filter(user_id=user_id),
        'qr_code_url': qr_code_url,
    }

    return render(request, 'purchase/order_summary.html', context)


from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Order

def order_history(request):
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    user_id = request.session.get('user_id')
    orders = Order.objects.filter(user_id=user_id).order_by('-order_date')
    context = {'orders': orders}
    return render(request, 'purchase/order_history.html', context)

from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from .models import Review, OrderItem
from products.models import Product
def submit_review(request, order_id):
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    order = get_object_or_404(Order, id=order_id, user_id=request.session.get('user_id'))

    # Ensure the order is delivered before allowing a review
    if order.status != 'delivered':
        return JsonResponse({'error': 'You can only review delivered items.'}, status=403)

    if request.method == 'POST':
        # Handle review submission for all products in the order
        for item_id, rating in request.POST.items():
            if item_id.startswith('rating_'):
                order_item_id = int(item_id.split('_')[1])
                comment = request.POST.get(f'comment_{order_item_id}', '')

                order_item = get_object_or_404(order.order_items, id=order_item_id)

                # Create the review
                Review.objects.create(
                    user=order.user,
                    product=order_item.batch.product,
                    order=order,
                    rating=rating,
                    comment=comment
                )
        return redirect('purchase:order_history')

    rating_range = range(1, 6)  # Pass the range to the template
    return render(request, 'purchase/submit_review.html', {'order': order, 'rating_range': rating_range})


from django.shortcuts import get_object_or_404, render
from .utils import ensure_user_logged_in

def product_reviews(request, product_id):
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product).order_by('-review_date')
    return render(request, 'products/product_reviews.html', {'product': product, 'reviews': reviews})

# views.py
from django.db.models import Q

def manage_reviews(request):
    # Check if the user is logged in
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    # Fetch all reviews with related user and product data
    reviews = Review.objects.select_related('user', 'product').all()

    # Get the search query from GET request
    search_query = request.GET.get('q', '').strip()

    if search_query:
        # Search for reviews containing the query in comment, user name, email, or product name
        reviews = reviews.filter(
            Q(comment__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(product__name__icontains=search_query)
        )

    # Sort reviews by the most recent review date
    reviews = reviews.order_by('-review_date')

    if request.method == 'POST':
        # Process admin actions like replying or deleting a review
        action = request.POST.get('action')
        review_id = request.POST.get('review_id')

        try:
            review = Review.objects.get(id=review_id)
            if action == 'reply':
                reply = request.POST.get('reply')
                # Save the reply to the review (update if already exists)
                review.reply = reply
                review.save()
            elif action == 'delete':
                review.delete()
        except Review.DoesNotExist:
            pass  # Handle case where the review doesn't exist

    return render(request, 'purchase/manage_reviews.html', {
        'reviews': reviews,
        'search_query': search_query
    })


# Function to ensure the user is logged in

# View Orders
def view_orders(request):
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    # Prefetch related `OrderItem` data for each `Order`
    orders = Order.objects.select_related('user').prefetch_related('order_items').all()

    return render(request, 'purchase/view_orders.html', {'orders': orders})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order

# Update Order Status
def update_order_status(request, order_id):
    """
    Updates the order status and handles related business logic.
    """
    if not ensure_user_logged_in(request):
        return JsonResponse({'error': 'Authentication required'}, status=403)
    
    try:
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        with transaction.atomic():
            # Handle status-specific logic
            if new_status == 'picked_up':
                if not order.assigned_delivery_person:
                    return JsonResponse({'error': 'No delivery person assigned'}, status=400)
                
            elif new_status == 'delivered':
                # Update delivery completion time
                order.delivery_date = timezone.now()
                
                # Update delivery person's status
                if order.assigned_delivery_person:
                    delivery_person = order.assigned_delivery_person
                    delivery_person.daily_order_count -= 1
                    delivery_person.status = 'available'
                    delivery_person.save()
                
            elif new_status == 'cancel':
                # Restore stock quantities
                for item in order.order_items.all():
                    if item.batch:
                        item.batch.stock_quantity += item.quantity
                        item.batch.save()
                
                # Update payment status if necessary
                if order.payment_status == 'Success':
                    # Implement refund logic here
                    pass
            
            # Update order status
            order.status = new_status
            order.save()
            
            # Send notifications based on status change
            # send_status_update_notification(order)
            
            return JsonResponse({
                'success': True,
                'message': f'Order status updated to {new_status}',
                'order_id': order.id,
                'status': new_status
            })
            
    except Exception as e:
        logger.error(f"Error updating order status: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'Failed to update order status',
            'details': str(e)
        }, status=500)

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Order, OrderItem, Login

def get_order_details(request, order_id):
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    order = get_object_or_404(Order, id=order_id)
    order_items = order.order_items.select_related('batch').all()

    # Accessing email from the Login table, using 'uid' field to reference User_Reg
    login_data = get_object_or_404(Login, uid=order.user)  # Use 'uid' to reference User_Reg in Login

    items = [
        {
            'product_name': item.product,
            'quantity': item.quantity,
            'total_price': item.get_total_price_with_discount()
        }
        for item in order_items
    ]

    # Passing order data to the template
    context = {
        'order': order,
        'order_items': items,
        'customer_email': login_data.email,  # Get email from the Login table
        'delivery_address': {
            'first_name': order.billing.first_name,
            'last_name': order.billing.last_name,
            'street_address': order.billing.street_address,
            'town_city': order.billing.town_city,
            'district': order.billing.district,
            'postcode_zip': order.billing.postcode_zip,
            'phone': order.billing.phone,
            'email': order.billing.email,
        }
    }

    return render(request, 'purchase/order_details.html', context)


from django.shortcuts import render
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils.dateparse import parse_date
import json

def decimal_to_float(value):
    return float(value) if isinstance(value, Decimal) else value

from datetime import datetime, timedelta
from django.db.models import Sum, Count
from django.shortcuts import render
from django.utils.dateparse import parse_date
import json

def decimal_to_float(value):
    """Convert Decimal to float for JSON serialization."""
    return float(value) if value else 0.0
def reports(request):
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    # Get date filters from request
    date_filter = request.GET.get("date_filter", "30_days")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    today = datetime.today()

    # Define the date range based on the selected filter
    if date_filter == "30_days":
        date_from = today - timedelta(days=30)
        date_to = today
    elif date_filter == "past_week":
        date_from = today - timedelta(days=7)
        date_to = today
    elif date_filter == "past_month":
        date_from = today.replace(day=1)
        date_to = today
    elif date_filter == "custom" and start_date and end_date:
        date_from = parse_date(start_date)
        date_to = parse_date(end_date)
    else:
        # Default to the last 30 days if no valid filter is selected
        date_from = today - timedelta(days=30)
        date_to = today

    # Sales Data
    sales_data = Order.objects.filter(order_date__range=(date_from, date_to), payment_status="Success").aggregate(
        total_sales=Sum('total_amount'), order_count=Count('id')
    )
    sales_data['total_sales'] = decimal_to_float(sales_data['total_sales'])

    # Total Purchased Products Analysis
    purchased_products = (
        OrderItem.objects.filter(order__order_date__range=(date_from, date_to), order__payment_status="Success")
        .values('product')  # Filter by product name in OrderItem
        .annotate(total_quantity=Sum('quantity'), total_spent=Sum('price'))
        .order_by('-total_quantity')
    )
    purchased_products_labels = [item['product'] for item in purchased_products]
    purchased_products_quantities = [item['total_quantity'] for item in purchased_products]
    for product in purchased_products:
        product['total_spent'] = decimal_to_float(product['total_spent'])

    # Order Trends
    order_trends = Order.objects.filter(order_date__range=(date_from, date_to)).values('status').annotate(count=Count('id'))
    order_trends_labels = [item['status'] for item in order_trends]
    order_trends_counts = [item['count'] for item in order_trends]

    # Top Customers
    top_customers = (
        Order.objects.filter(order_date__range=(date_from, date_to), payment_status="Success")
        .values('user__first_name', 'user__last_name')
        .annotate(total_spent=Sum('total_amount'))
        .order_by('-total_spent')[:5]
    )
    for customer in top_customers:
        customer['total_spent'] = decimal_to_float(customer['total_spent'])

    # Monthly Sales (Last 6 Months)
    monthly_sales_labels = []
    monthly_sales_data = []
    for i in range(6):
        month_start = today.replace(day=1) - timedelta(days=i * 30)
        month_end = (month_start + timedelta(days=30)).replace(day=1)
        month_sales = Order.objects.filter(order_date__range=(month_start, month_end), payment_status="Success").aggregate(
            total_sales=Sum('total_amount')
        )
        monthly_sales_labels.append(month_start.strftime("%B"))
        monthly_sales_data.append(decimal_to_float(month_sales["total_sales"] or 0))

    # Top Trending Products
    top_trending_products = purchased_products[:5]  # Get the top 5 trending products
    trending_products_labels = [item['product'] for item in top_trending_products]
    trending_products_quantities = [item['total_quantity'] for item in top_trending_products]

    # Context for rendering
    context = {
        'sales_data': sales_data,
        'purchased_products': purchased_products,
        'top_trending_products': top_trending_products,
        'purchased_products_labels': json.dumps(purchased_products_labels),
        'purchased_products_quantities': json.dumps(purchased_products_quantities),
        'trending_products_labels': json.dumps(trending_products_labels),
        'trending_products_quantities': json.dumps(trending_products_quantities),
        'order_trends_labels': json.dumps(order_trends_labels),
        'order_trends_counts': json.dumps(order_trends_counts),
        'top_customers': top_customers,
        'monthly_sales_labels': json.dumps(monthly_sales_labels),
        'monthly_sales_data': json.dumps(monthly_sales_data),
        'date_filter': date_filter,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'purchase/reports.html', context)

def generate_report(request):
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    # Get date filters from request
    date_filter = request.GET.get("date_filter", "30_days")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    today = datetime.today()

    # Define the date range based on the selected filter
    if date_filter == "30_days":
        date_from = today - timedelta(days=30)
        date_to = today
    elif date_filter == "past_week":
        date_from = today - timedelta(days=7)
        date_to = today
    elif date_filter == "past_month":
        date_from = today.replace(day=1)
        date_to = today
    elif date_filter == "custom" and start_date and end_date:
        date_from = parse_date(start_date)
        date_to = parse_date(end_date)
    else:
        date_from = today - timedelta(days=30)
        date_to = today

    # Fetch orders and order items data based on date range
    orders = Order.objects.filter(order_date__range=(date_from, date_to))
    order_items = OrderItem.objects.filter(order__order_date__range=(date_from, date_to))

    context = {
        'orders': orders,
        'order_items': order_items,
        'date_filter': date_filter,
        'start_date': start_date,
        'end_date': end_date,
    }

    # Standard page rendering for non-AJAX requests
    return render(request, 'purchase/genetate_repaort.html', context)


from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from .models import OrderItem
from datetime import datetime, timedelta

def generate_order_pdf(request):
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    date_filter = request.GET.get("date_filter", "30_days")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # Date range logic here
    today = datetime.today()
    if date_filter == "30_days":
        date_from = today - timedelta(days=30)
        date_to = today
    else:
        date_from, date_to = today - timedelta(days=7), today

    order_items = OrderItem.objects.filter(order__order_date__range=(date_from, date_to))

    context = {
        'order_items': order_items,
        'start_date': start_date or date_from,
        'end_date': end_date or date_to,
    }

    # Render PDF
    html = render_to_string('purchase/order_report_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="order_report.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response






















from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Order, Login, Cart
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.units import inch
from io import BytesIO

def download_bill(request, order_id):
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    # Get user and order data
    user = get_object_or_404(Login, login_id=request.session.get('user_id'))
    order = get_object_or_404(Order, id=order_id, user_id=user.uid_id)
    order_items = order.order_items.all()

    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=30,  # Reduced top margin for better logo placement
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Colors
    brand_green = colors.HexColor("#2E7D32")
    accent_green = colors.HexColor("#4CAF50")
    text_gray = colors.HexColor("#484848")
    light_gray = colors.HexColor("#F5F5F5")
    
    # Custom Styles
    title_style = ParagraphStyle(
        'BrandTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=brand_green,
        spaceAfter=20,
        alignment=1,
        fontName="Helvetica-Bold"
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=accent_green,
        spaceBefore=10,
        spaceAfter=20,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=brand_green,
        spaceBefore=15,
        spaceAfter=8,
        fontName="Helvetica-Bold"
    )
    
    normal_style = ParagraphStyle(
        'ContentText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=text_gray,
        spaceBefore=4,
        spaceAfter=4,
        fontName="Helvetica"
    )
    
    # Add logo
    try:
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path)
            # Scale logo to appropriate size (2 inch diameter)
            aspect = logo.imageWidth / logo.imageHeight
            logo.drawWidth = 2 * inch
            logo.drawHeight = 2 * inch / aspect
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 15))
    except Exception as e:
        print(f"Logo loading error: {e}")

    # Header with border
    header_table = Table([
        [Paragraph("Enchanted Eden", title_style)],
        [Paragraph("Plant Nursery", subtitle_style)],
    ], colWidths=[440])
    
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, -1), light_gray),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 1, brand_green),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # Bill Info in an elegant box
    bill_info = Table([
        ['Invoice No:', f'#{order.id}', 'Date:', order.order_date.strftime('%B %d, %Y')],
        ['Status:', order.status.title(), 'Payment:', order.payment_status]
    ], colWidths=[70, 150, 70, 150])
    
    bill_info.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), text_gray),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, brand_green),
    ]))
    elements.append(bill_info)
    elements.append(Spacer(1, 20))

    # Enhanced customer details with better styling
    elements.append(Paragraph("Billing Details", heading_style))
    customer_details = [
        [Paragraph(f"""
        <b>{order.billing.first_name} {order.billing.last_name}</b><br/>
        {order.billing.street_address}<br/>
        {order.billing.town_city}, {order.billing.district}<br/>
        PIN: {order.billing.postcode_zip}<br/>
        Phone: {order.billing.phone}<br/>
        Email: {order.billing.email}
        """, normal_style)]
    ]
    customer_table = Table(customer_details, colWidths=[440])
    customer_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), text_gray),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (-1, -1), light_gray),
        ('BOX', (0, 0), (-1, -1), 1, brand_green),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 20))

    # Enhanced order items table
    elements.append(Paragraph("Order Details", heading_style))
    table_data = [['Product', 'Qty', 'Price', 'Discount', 'Total']]
    for item in order_items:
        row = [
            item.product,
            str(item.quantity),
            f"₹{item.price}",
            f"{item.discount}%" if item.discount else "-",
            f"₹{item.get_total_price_with_discount():.2f}"
        ]
        table_data.append(row)
    
    order_table = Table(table_data, colWidths=[200, 50, 70, 60, 60])
    order_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), brand_green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), text_gray),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, brand_green),
        ('BOX', (0, 0), (-1, -1), 1.5, brand_green),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_gray]),
    ]))
    elements.append(order_table)
    elements.append(Spacer(1, 15))

    # Summary calculations
    actual_subtotal = sum(item.get_total_price() for item in order_items)
    total_discount = sum((item.get_total_price() * item.discount / 100) for item in order_items)
    delivery_price = 50
    final_total = order.total_amount

    # Enhanced summary table
    summary_data = [
        ['Subtotal:', f"₹{actual_subtotal:.2f}"],
        ['Discount:', f"₹{total_discount:.2f}"],
        ['Delivery:', f"₹{delivery_price:.2f}"],
        ['Total:', f"₹{final_total:.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[340, 100])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('TEXTCOLOR', (0, 0), (-1, -2), text_gray),
        ('TEXTCOLOR', (-1, -1), (-1, -1), brand_green),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEABOVE', (0, -1), (-1, -1), 1, brand_green),
        ('BACKGROUND', (0, -1), (-1, -1), light_gray),
    ]))
    elements.append(summary_table)

    # Enhanced footer with border
    elements.append(Spacer(1, 30))
    footer_text = """Thank you for shopping with us!
    For support: +91 9876543210 | support@enchantededen.com"""
    
    footer_table = Table([[Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        alignment=1,
        textColor=accent_green,
        fontSize=8,
        fontName="Helvetica"
    ))]], colWidths=[440])
    
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, -1), light_gray),
        ('BOX', (0, 0), (-1, -1), 1, brand_green),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(footer_table)

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return HttpResponse(
        buffer,
        content_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="EE_Invoice_{order_id}.pdf"'}
    )

def generate_qr(order_id):
    # Define the directory path
    qr_directory = os.path.join(settings.MEDIA_ROOT, 'qr_codes')

    # Check if the directory exists, if not, create it
    if not os.path.exists(qr_directory):
        os.makedirs(qr_directory)

    # Generate the QR code with the URL to confirm delivery
    qr = qrcode.make(f"http://localhost:8000/delivery/confirm_delivery/{order_id}")

    # Save the QR code image
    qr_path = os.path.join(qr_directory, f"order_{order_id}.png")
    qr.save(qr_path)

    # Return the URL path for the QR code
    return os.path.join(settings.MEDIA_URL, 'qr_codes', f"order_{order_id}.png")
