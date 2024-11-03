# purchase/utils.py
def calculate_cart_total(cart):
    total = 0
    for item in cart.items.all():
        # Ensure we are accessing the correct model field if using Batch
        batch = item.batch  # Assuming 'batch' is the field linking CartItem to Batch
        total += batch.price * item.quantity
    return total
