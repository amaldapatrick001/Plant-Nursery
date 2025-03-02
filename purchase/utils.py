# purchase/utils.py
def calculate_cart_total(cart):
    total = 0
    for item in cart.items.all():
        # Ensure we are accessing the correct model field if using Batch
        batch = item.batch  # Assuming 'batch' is the field linking CartItem to Batch
        total += batch.price * item.quantity
    return total
# utils.py
from django.shortcuts import redirect

def ensure_user_logged_in(request):
    # Check if 'user_id' exists in the session
    return 'user_id' in request.session
