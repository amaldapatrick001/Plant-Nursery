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

    path('order-history/', views.order_history, name='order_history'),
   #admin
    path('orders/', views.view_orders, name='view_orders'),
    path('orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
path('order_details/<int:order_id>/', views.get_order_details, name='view_order_details'),
# Add this to your `urlpatterns`
path('reports/', views.reports, name='reports'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('generate_order_pdf/', views.generate_order_pdf, name='generate_order_pdf'),
    path('submit-review/<int:order_id>/', views.submit_review, name='submit_review'),
path('product-reviews/<int:product_id>/', views.product_reviews, name='product_reviews'),
path('admin/manage_reviews/', views.manage_reviews, name='manage_reviews'),
path('generate_qr/<int:order_id>/', views.generate_qr, name='generate_qr'),
]
