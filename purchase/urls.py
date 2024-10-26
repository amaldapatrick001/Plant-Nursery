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
    path('place_order/', views.CheckoutView.as_view(), name='place_order'),  # Place order through CheckoutView post
    
    # Order Summary and Confirmation Pages
    path('order_summary/<int:order_id>/', views.OrderSummaryView.as_view(), name='order_summary'),
    path('order_confirmation/<int:order_id>/', views.OrderConfirmationView.as_view(), name='order_confirmation'),

    # Payment Related URLs
    path('payment/<int:order_id>/', views.PaymentGatewayView.as_view(), name='payment_gateway'),  # Payment gateway page
    path('payment_method/', views.PaymentMethodView.as_view(), name='payment_method'),  # Display payment methods

    # Address Related URLs
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),  # Delete address
    path('set_delivery_address/', views.set_delivery_address, name='set_delivery_address'),  # Set delivery address
    
    path("initiate-payment/<int:order_id>/", views.initiate_payment, name="initiate_payment"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("payment-failure/", views.payment_failure, name="payment_failure"),
]