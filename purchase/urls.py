from django.urls import path
from . import views

app_name = 'purchase'

urlpatterns = [
    path('add/<int:batch_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
     path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),  # Add this line for checkout
    path('place_order/',views.place_order,name='place_order'),
]