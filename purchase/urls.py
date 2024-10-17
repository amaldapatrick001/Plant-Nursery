from django.urls import path
from . import views

app_name = 'purchase'

urlpatterns = [
    path('add/<int:batch_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
     path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order_summary/<int:order_id>/', views.OrderSummaryView.as_view(), name='order_summary'),
    path('order_confirmation/<int:order_id>/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
    path('payment_gateway/<int:order_id>/', views.PaymentGatewayView.as_view(), name='payment_gateway'),
]
