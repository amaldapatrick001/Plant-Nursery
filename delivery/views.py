from multiprocessing import context
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from userauths.models import DeliveryPersonnel, Login, User_Reg
from purchase.models import Billing, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

# View Undelivered Orders
def view_undelivered_orders(request):
    # Fetch undelivered orders (status is 'pending')
    undelivered_orders = Order.objects.filter(status='pending')

    # Fetch available delivery personnel
    available_delivery_personnel = DeliveryPersonnel.objects.filter(status='available')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        delivery_person_id = request.POST.get('delivery_person_id')

        if order_id and delivery_person_id:
            # Get the order and delivery personnel based on the IDs
            order = get_object_or_404(Order, id=order_id, status='pending')
            delivery_person = get_object_or_404(DeliveryPersonnel, delivery_id=delivery_person_id, status='available')

            # Assign the delivery person to the order
            order.status = 'assigned'
            order.assigned_delivery_person = delivery_person
            order.save()

            # Update delivery personnel details
            
            delivery_person.assigned_orders += 1
            delivery_person.save()

            messages.success(request, f"Order {order_id} has been assigned to {delivery_person.user.first_name} {delivery_person.user.last_name}.")
            return redirect('delivery:view_undelivered_orders')

    context = {
        'undelivered_orders': undelivered_orders,
        'available_delivery_personnel': available_delivery_personnel,
    }
    return render(request, 'Deliveryboy/undelivered_orders.html', context)






# View Delivery History
def view_delivery_history(request):
    # Fetch orders with statuses: 'assigned', 'picked_up', 'in_transit', 'delivered'
    delivery_history = Order.objects.filter(status__in=['assigned', 'picked_up', 'in_transit', 'delivered']).select_related('assigned_delivery_person', 'user')

    context = {
        'delivery_history': delivery_history,
    }
    return render(request, 'Deliveryboy/delivery_history.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dview_assigned_orders(request):
    """View for delivery personnel to see their assigned orders"""
    if 'user_id' not in request.session:
        return redirect('userauths:login')

    login_user = Login.objects.get(login_id=request.session['user_id'])
    user = login_user.uid
    delivery_personnel = get_object_or_404(DeliveryPersonnel, user=user)

    # Get orders in different stages
    assigned_orders = Order.objects.filter(
        assigned_delivery_person=delivery_personnel,
        status='assigned'
    ).select_related('user', 'billing')

    picked_up_orders = Order.objects.filter(
        assigned_delivery_person=delivery_personnel,
        status='picked_up'
    ).select_related('user', 'billing')

    in_transit_orders = Order.objects.filter(
        assigned_delivery_person=delivery_personnel,
        status='in_transit'
    ).select_related('user', 'billing')

    context = {
        'assigned_orders': assigned_orders,
        'picked_up_orders': picked_up_orders,
        'in_transit_orders': in_transit_orders,
        'delivery_personnel': delivery_personnel
    }
    
    return render(request, 'Deliveryboy/dassigned_orders.html', context)
    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dupdate_order_status(request, order_id):
    """Update order status and location"""
    if 'user_id' not in request.session:
        return redirect('userauths:login')

    try:
        login_user = Login.objects.get(login_id=request.session['user_id'])
        user = login_user.uid
        delivery_personnel = get_object_or_404(DeliveryPersonnel, user=user)
        order = get_object_or_404(Order, 
                                id=order_id, 
                                assigned_delivery_person=delivery_personnel)

        # Status progression logic
        status_flow = {
            'assigned': 'picked_up',
            'picked_up': 'in_transit',
            'in_transit': 'delivered'
        }

        if order.status in status_flow:
            new_status = status_flow[order.status]
            order.status = new_status
            
            if new_status == 'delivered':
                order.delivery_date = timezone.now()
                delivery_personnel.complete_order()
            
            order.save()
            
            messages.success(request, 
                           f"Order status updated to {new_status.replace('_', ' ').title()}")
        
        return redirect('delivery:view_assigned_orders')

    except Exception as e:
        logger.error(f"Error in dupdate_order_status: {str(e)}")
        messages.error(request, "An error occurred while updating order status.")
        return redirect('delivery:view_assigned_orders')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ddelivery_history(request):
    """View delivery history for completed orders"""
    if 'user_id' not in request.session:
        return redirect('userauths:login')

    try:
        login_user = Login.objects.get(login_id=request.session['user_id'])
        user = login_user.uid
        delivery_personnel = get_object_or_404(DeliveryPersonnel, user=user)

        completed_orders = Order.objects.filter(
            assigned_delivery_person=delivery_personnel,
            status__in=['delivered', 'return']
        ).select_related('user', 'billing').order_by('-delivery_date')

        return render(request, 'Deliveryboy/ddelivery_history.html', 
                     {'orders': completed_orders})

    except Exception as e:
        logger.error(f"Error in ddelivery_history: {str(e)}")
        return render(request, 'Deliveryboy/ddelivery_history.html', 
                     {'orders': [], 'error': str(e)})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_delivery_location(request):
    """Update delivery personnel's current location"""
    if request.method == 'POST' and request.is_ajax():
        try:
            delivery_personnel = get_object_or_404(
                DeliveryPersonnel, 
                user__login__login_id=request.session['user_id']
            )
            
            delivery_personnel.current_latitude = request.POST.get('latitude')
            delivery_personnel.current_longitude = request.POST.get('longitude')
            delivery_personnel.save()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Location update error: {str(e)}")
            return JsonResponse({'status': 'error'}, status=400)
    
    return JsonResponse({'status': 'error'}, status=405)

def delivery_overview(request):
#     # Ensure the user is logged in
#     if 'user_id' not in request.session:
#         return redirect('userauths:login')

#     # Get the user from the session using the correct field (uid)
#     user_id = request.session['user_id']
#     try:
#         user = User_Reg.objects.get(uid=user_id)
#     except User_Reg.DoesNotExist:
#         return redirect('userauths:login')  # Handle if user doesn't exist

#     # Get the relevant orders based on status for the logged-in user
#     delivered_orders = Order.objects.filter(user=user, status='delivered')
#     canceled_orders = Order.objects.filter(user=user, status='cancel')
#     returned_orders = Order.objects.filter(user=user, status='return')

#     # Fetch the delivery personnel data (if needed)
#     if user.status and hasattr(user, 'deliverypersonnel'):
#         delivery_personnel = user.deliverypersonnel
#         assigned_orders = Order.objects.filter(assigned_delivery_person=delivery_personnel)
#         completed_orders = assigned_orders.filter(status='delivered')
#         canceled_or_returned_orders = assigned_orders.filter(status__in=['cancel', 'return'])
#     else:
#         delivery_personnel = None
#         assigned_orders = completed_orders = canceled_or_returned_orders = None

#     # Return the data to the template
#     context = {
#         'delivered_orders': delivered_orders,
#         'canceled_orders': canceled_orders,
#         'returned_orders': returned_orders,
#         'delivery_personnel': delivery_personnel,
#         'assigned_orders': assigned_orders,
#         'completed_orders': completed_orders,
#         'canceled_or_returned_orders': canceled_or_returned_orders,
#     }
    
     return render(request, 'delivery/ddelivery_overview.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def confirm_delivery_page(request, order_id):
    """Renders the QR scanner page for delivery confirmation"""
    return render(request, 'Deliveryboy/confirm_delivery.html', {'order_id': order_id})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def confirm_delivery(request):
    """Processes the scanned QR code and updates order status"""
    if request.method == "POST":
        scanned_order_id = request.POST.get("order_id")

        try:
            order = get_object_or_404(Order, id=scanned_order_id, status="in_transit")

            # Mark order as delivered
            order.status = "delivered"
            order.save()

            messages.success(request, f"Order {order.id} has been marked as delivered!")
            return redirect("delivery:view_assigned_orders")
        
        except Exception as e:
            messages.error(request, "Invalid Order ID or Order not in transit!")
            return redirect("delivery:confirm_delivery_page", order_id=scanned_order_id)

    return JsonResponse({"status": "error", "message": "Invalid Request"}, status=400)


# Placeholder for assigned orders view
def assigned_orders():
    pass


# Placeholder for updating the order status view
def update_order_status():
    pass

# Placeholder for displaying order details view
def order_details():
    pass

def update_delivery_location():
    pass

# Placeholder for tracking an order view
def order_tracking_view():
    pass
