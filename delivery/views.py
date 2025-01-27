from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from userauths.models import DeliveryPersonnel, Login, User_Reg
from purchase.models import Billing, Order, OrderItem
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


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from purchase.models import Order
from userauths.models import DeliveryPersonnel
import logging

logger = logging.getLogger(__name__)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dview_assigned_orders(request):
    if 'user_id' not in request.session:
        return redirect('userauths:login')

    try:
        login_user = Login.objects.get(login_id=request.session['user_id'])
        user = login_user.uid  # Get the User_Reg object

        # Ensure the user is delivery personnel
        delivery_personnel = get_object_or_404(DeliveryPersonnel, user=user)

        assigned_orders = Order.objects.filter(assigned_delivery_person=delivery_personnel, status='assigned')
        picked_up_orders = Order.objects.filter(assigned_delivery_person=delivery_personnel, status='picked_up')
        in_transit_orders = Order.objects.filter(assigned_delivery_person=delivery_personnel, status='in_transit')

        return render(request, 'Deliveryboy/dassigned_orders.html', {
            'assigned_orders': assigned_orders,
            'picked_up_orders': picked_up_orders,
            'in_transit_orders': in_transit_orders,
            'delivery_personnel': delivery_personnel
        })
    
    except (Login.DoesNotExist, DeliveryPersonnel.DoesNotExist) as e:
        logger.error(f"Error fetching orders: {str(e)}")
        return redirect('userauths:login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dupdate_order_status(request, order_id):
    if 'user_id' not in request.session:
        return redirect('userauths:login')

    try:
        # Get the login object first
        login_user = Login.objects.get(login_id=request.session['user_id'])
        user = login_user.uid  # Get the User_Reg object

        # Ensure the user is delivery personnel
        delivery_personnel = get_object_or_404(DeliveryPersonnel, user=user)

        # Get the order and ensure it is assigned to the current delivery personnel
        order = get_object_or_404(Order, id=order_id, assigned_delivery_person=delivery_personnel)

        # Get the latest billing address for this order
        billing = Billing.objects.filter(user=order.user).latest('id')
        delivery_location = f"{billing.street_address}, {billing.town_city}, {billing.district}, {billing.postcode_zip}"

        # Determine the next status based on current status
        if order.status == 'assigned':
            new_status = 'picked_up'
        elif order.status == 'picked_up':
            new_status = 'in_transit'
        else:
            messages.warning(request, "Order status cannot be updated further.")
            return redirect('delivery:view_assigned_orders')

        # Update the order status
        order.status = new_status
        order.save()

        # Log the status update
        messages.success(request, f"Order {order.id} status updated to {new_status.replace('_', ' ').title()}.")
        logger.info(f"Order {order.id} status updated to {new_status} by {delivery_personnel.user.first_name}. Delivery location: {delivery_location}")

        return redirect('delivery:view_assigned_orders')

    except Login.DoesNotExist:
        messages.error(request, "Please login to continue.")
        return redirect('userauths:login')
    except DeliveryPersonnel.DoesNotExist:
        messages.error(request, "Access denied. You are not authorized as delivery personnel.")
        return redirect('userauths:login')
    except Order.DoesNotExist:
        messages.error(request, "Order not found or not assigned to you.")
        return redirect('delivery:view_assigned_orders')
    except Billing.DoesNotExist:
        messages.error(request, "Billing information not found for this order.")
        return redirect('delivery:view_assigned_orders')
    except Exception as e:
        logger.error(f"Error updating order status: {str(e)}")
        messages.error(request, "An error occurred while updating the order status.")
        return redirect('delivery:view_assigned_orders')

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

def ddelivery_history(request):
    # Check if the user is logged in
    if 'user_id' not in request.session:
        return redirect('userauths:login')

    try:
        # Get the logged-in delivery personnel
        login_user = Login.objects.get(login_id=request.session['user_id'])
        user = login_user.uid  # Get the User_Reg object
        delivery_personnel = get_object_or_404(DeliveryPersonnel, user=user)

        # Fetch all delivered or returned orders assigned to the delivery personnel
        orders = Order.objects.filter(
            assigned_delivery_person=delivery_personnel,
            status__in=['delivered', 'return']
        ).order_by('-delivery_date')

        return render(request, 'Deliveryboy/ddelivery_history.html', {'orders': orders})
    except Login.DoesNotExist:
        return redirect('userauths:login')
    except DeliveryPersonnel.DoesNotExist:
        return redirect('userauths:login')
    except Exception as e:
        return render(request, 'Deliveryboy/ddelivery_history.html', {'orders': [], 'error': str(e)})
    
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
