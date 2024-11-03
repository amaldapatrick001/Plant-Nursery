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
    path('set_delivery_address/', views.set_delivery_address, name='set_delivery_address'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('razorpay_checkout/', views.razorpay_checkout, name='razorpay_checkout'),
    path('order_summary/<int:order_id>/', views.order_summary, name='order_summary'),  # Added missing comma
    path('order/<int:order_id>/download-bill/', views.download_bill, name='download_bill'),
    path('download-bill/<int:order_id>/', views.download_bill, name='download_bill'),
    path('order/<int:order_id>/download-bill/', views.download_bill, name='download_bill'),
]