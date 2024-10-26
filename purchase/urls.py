from django.urls import path
from . import views

app_name = 'purchase'

urlpatterns = [
    path('add/<int:batch_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout and Order Related URLs
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),  
     path('payment/<int:order_id>/', views.PaymentGatewayView.as_view(), name='payment_gateway'),  # Payment gateway page
    path('payment/success/', views.payment_success, name='payment_success'),  # Payment success callback
    path('payment/failure/', views.payment_failure, name='payment_failure'),  # Payment failure callback
    path('order/summary/<int:order_id>/', views.OrderSummaryView.as_view(), name='order_summary'),  # Order summary page
    path('order/confirmation/<int:order_id>/', views.OrderConfirmationView.as_view(), name='order_confirmation'),  # Order confirmation page
    path('set-delivery-address/', views.set_delivery_address, name='set_delivery_address'),
    path('delete_address/<int:id>/', views.delete_address_view, name='delete_address'),  # Ensure this pattern exists
    
]