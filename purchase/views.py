from datetime import timedelta
from multiprocessing import context
from django.utils import timezone
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views import View
from purchase.forms import CheckoutForm
from userauths.models import Login, User_Reg
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
    # Fetch the incomplete cart for the current user
    cart = Cart.objects.filter(user_id=request.session.get('user_id'), is_completed=False).first()
    
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

    cart = Cart.objects.filter(user_id=request.session.get('user_id'), is_completed=False).first()

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




from django.contrib import messages
from django.shortcuts import redirect

def ensure_user_logged_in(request):
    """Ensure the user is logged in; if not, redirect to login with an error message."""
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to proceed.')
        return False
    return True
from django.shortcuts import get_object_or_404, redirect, reverse, render
from django.views import View
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Billing, Cart, Order
from .forms import CheckoutForm
from .utils import calculate_cart_total





# Ensure that all views check if the user is logged in
class CheckoutView(View):
    def get(self, request):
        if not ensure_user_logged_in(request):
            return redirect('userauths:login')

        user_id = request.session['user_id']
        addresses = Billing.objects.filter(user_id=user_id)
        form = CheckoutForm()
        cart = Cart.objects.filter(user_id=user_id, is_completed=False).first()
        cart_items = cart.items.all() if cart else []

        if not cart_items:
            messages.info(request, 'Your cart is empty.')
            return redirect('products:cproduct_list')

        actual_subtotal = sum(item.get_total_price() for item in cart_items)
        total_discount = sum(item.get_discount_amount() for item in cart_items)
        delivery_price = 50

        total_after_discount = actual_subtotal - total_discount
        total_price_with_delivery_and_discount = total_after_discount + delivery_price
        total_price_with_delivery_and_discounts = int((total_after_discount + delivery_price) * 100)

        selected_address_id = request.session.get('selected_address_id', None)

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
            'selected_address_id': selected_address_id,
        })
from django.shortcuts import get_object_or_404, redirect, reverse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Billing, Cart, Order
from .utils import calculate_cart_total


@require_POST
def set_delivery_address(request):
    # Ensure user is logged in
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    # Retrieve user and selected address ID
    user_id = request.session['user_id']
    address_id = request.POST.get('selected_address')

    # Ensure an address was selected
    if not address_id:
        messages.error(request, "Please select a billing address.")
        return redirect('purchase:checkout')

    # Fetch the selected billing address and active cart
    billing_address = get_object_or_404(Billing, id=address_id, user_id=user_id)
    cart = get_object_or_404(Cart, user_id=user_id, is_completed=False)
    total_amount = calculate_cart_total(cart)

    # Retrieve or create an order
    order_id = request.session.get('current_order_id')
    order = Order.objects.filter(id=order_id, user_id=user_id).first()

    if order:
        # Update the existing order
        order.billing = billing_address  # Update the billing address
        order.total_amount = total_amount  # Ensure total amount is updated
        order.save()
    else:
        # Create a new order if one doesn't exist in session
        order = Order.objects.create(
            user_id=user_id,
            billing=billing_address,
            cart=cart,
            total_amount=total_amount,
        )
        request.session['current_order_id'] = order.id  # Save new order ID in session

    # Store the selected address in the session
    request.session['selected_address_id'] = billing_address.id

    # Confirm address update to user
    messages.success(request, "Delivery address set successfully.")
    return redirect(reverse('purchase:checkout'))





@require_POST
def delete_address(request, address_id):
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    user_id = request.session['user_id']
    address = get_object_or_404(Billing, id=address_id, user_id=user_id)
    address.delete()
    messages.success(request, "Address deleted successfully.")
    return redirect('purchase:checkout')
@require_POST
def razorpay_checkout(request):
    if not ensure_user_logged_in(request):
        return JsonResponse({'success': False, 'error': 'User not logged in'}, status=403)

    user_id = request.session['user_id']
    data = json.loads(request.body)
    
    razorpay_payment_id = data.get('razorpay_payment_id')
    order_id = request.session.get('current_order_id')  # Retrieve from session

    order = get_object_or_404(Order, id=order_id, user_id=user_id)

    if razorpay_payment_id:
        order.razorpay_order_id = razorpay_payment_id
        order.status = "Processing"  # Update status after successful payment
        order.payment_status = "Success"  # Update payment status
        order.payment_date = timezone.now()  # Correctly using Django's timezone
        
        # Calculate delivery date (order_date + 5 days)
        order.delivery_date = order.order_date + timedelta(days=5)

        # Calculate totals
        cart = get_object_or_404(Cart, id=order.cart.id, user_id=user_id)
        actual_subtotal = sum(item.get_total_price() for item in cart.items.all())
        total_discount = sum(item.get_discount_amount() for item in cart.items.all())
        delivery_price = 50  # Set your delivery price calculation logic here
        total_price_with_delivery_and_discount = actual_subtotal - total_discount + delivery_price
        
        # Update the total amount in the order
        order.total_amount = total_price_with_delivery_and_discount
        
        order.save()  # Save all changes
        
        return JsonResponse({'success': True, 'order_id': order.id})
    
    return JsonResponse({'success': False, 'error': 'Payment failed'}, status=400)




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order, Login, Cart
from .utils import calculate_cart_total  # Assuming you have a utility function for cart total

def order_summary(request, order_id):
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    user_id = request.session.get('user_id')
    user = get_object_or_404(Login, login_id=user_id)

    # Fetch the order based on order_id and user_id
    order = get_object_or_404(Order, id=order_id, user_id=user.uid_id)

    # Retrieve cart items associated with the order
    cart = get_object_or_404(Cart, id=order.cart.id, user_id=user.uid_id)  # Assuming order has a cart field

    # Calculate the required totals
    actual_subtotal = sum(item.get_total_price() for item in cart.items.all())
    total_discount = sum(item.get_discount_amount() for item in cart.items.all())
    delivery_price = 50  # This can be dynamic based on your logic
    total_price_with_delivery_and_discount = actual_subtotal - total_discount + delivery_price

    # Prepare context for rendering the template
    context = {
        'order': order,
        'cart_items': cart.items.all(),
        'actual_subtotal': actual_subtotal,
        'total_discount': total_discount,
        'delivery_price': delivery_price,
        'total_price_with_delivery_and_discount': total_price_with_delivery_and_discount,
        'selected_address_id': request.session.get('selected_address_id'),  # Assuming you need this
        'user_addresses': Billing.objects.filter(user_id=user_id),  # Fetching user's addresses
    }

    return render(request, 'purchase/order_summary.html', context)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Order, Login, Cart
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from io import BytesIO

def download_bill(request, order_id):
    # Ensure the user is logged in
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('userauths:login')

    # Retrieve the user using the Login model
    user = get_object_or_404(Login, login_id=user_id)

    # Fetch the order associated with the user
    order = get_object_or_404(Order, id=order_id, user_id=user.uid_id)

    # Retrieve the cart associated with the order
    cart = get_object_or_404(Cart, id=order.cart.id, user_id=user.uid_id)

    # Create a PDF response
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Define custom colors to match HTML theme
    primary_color = colors.HexColor("#4CAF50")
    secondary_color = colors.HexColor("#388E3C")
    accent_color = colors.HexColor("#8BC34A")

    # Custom styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="Title",
        fontSize=26,
        leading=30,
        alignment=1,
        textColor=primary_color,
        fontName="Helvetica-Bold"
    )
    subtitle_style = ParagraphStyle(
        name="Subtitle",
        fontSize=12,
        leading=14,
        textColor=secondary_color
    )
    normal_style = ParagraphStyle(
        name="Normal",
        fontSize=10,
        leading=12,
        textColor=colors.black
    )
    total_style = ParagraphStyle(
        name="Total",
        fontSize=12,
        leading=14,
        textColor=primary_color,
        fontName="Helvetica-Bold"
    )

    # Add logo at the top
    logo_path = "E:/PN - Copy/PlantNursery/static/images/logo.png"
    logo = Image(logo_path, width=100, height=50)
    logo.hAlign = 'CENTER'
    elements.append(logo)
    elements.append(Spacer(1, 12))

    # Add shop name and details
    elements.append(Paragraph("Enchanted Eden Plant Nursery", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Address: Your Shop Address", subtitle_style))
    elements.append(Paragraph("Contact: Your Contact Number", subtitle_style))
    elements.append(Paragraph("Email: Your Email", subtitle_style))
    elements.append(Spacer(1, 20))

    # Add order summary
    elements.append(Paragraph("Order Summary", ParagraphStyle(name="Heading", fontSize=16, textColor=primary_color)))
    elements.append(Spacer(1, 10))
    order_details = [
        f"Status: {order.status}",
        f"Order Date: {order.order_date.strftime('%B %d, %Y')}",
        f"Estimated Delivery Date: {order.delivery_date.strftime('%B %d, %Y') if order.delivery_date else 'N/A'}",
        f"Payment Status: {order.payment_status}",
        f"Total Amount: ₹{order.total_amount}",
    ]
    for detail in order_details:
        elements.append(Paragraph(detail, normal_style))
    elements.append(Spacer(1, 20))

    # Add items in the order as a table
    item_data = [['Product Name', 'Quantity', 'Price', 'Total']]
    for item in cart.items.all():
        item_data.append([
            item.batch.product.name,
            item.quantity,
            f"₹{item.batch.price}",
            f"₹{item.get_total_price()}"
        ])

    item_table = Table(item_data, colWidths=[200, 60, 80, 80])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(item_table)

    # Calculate totals
    actual_subtotal = sum(item.get_total_price() for item in cart.items.all())
    total_discount = sum(item.get_discount_amount() for item in cart.items.all())
    delivery_price = 50  # Set dynamically based on your logic
    total_price_with_delivery_and_discount = actual_subtotal - total_discount + delivery_price

    # Add totals with a new style
    elements.append(Spacer(1, 20))
    totals_data = [
        ["Subtotal", f"₹{actual_subtotal}"],
        ["Discount", f"₹{total_discount}"],
        ["Delivery Fee", f"₹{delivery_price}"],
        ["Grand Total", f"₹{total_price_with_delivery_and_discount}"]
    ]
    totals_table = Table(totals_data, colWidths=[350, 100])
    totals_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E0E0E0")),  # Light background for all rows
        ('TEXTCOLOR', (0, 0), (-1, -2), colors.black),  # Black text for subtotal and discount rows
        ('TEXTCOLOR', (-1, -1), (-1, -1), primary_color),  # Color for Grand Total row
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Set font
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),  # Right-align text
        ('FONTSIZE', (0, 0), (-1, -1), 12),  # Font size
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, -1), (-1, -1), 1, primary_color),  # Line above Grand Total
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.grey),  # Divider line between rows
    ]))
    elements.append(totals_table)

    # Build the PDF
    pdf.build(elements)

    # Return PDF as response
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', headers={'Content-Disposition': f'attachment; filename="bill_{order_id}.pdf"'})
