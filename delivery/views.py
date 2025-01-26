from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from userauths.models import DeliveryPersonnel
from purchase.models import Order, OrderItem
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
