from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('assigned-orders/', views.assigned_orders, name='assigned_orders'),
    path('delivery-history/', views.delivery_history, name='delivery_history'),
    path('update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('order-details/<int:order_id>/', views.order_details, name='order_details'),
    path('assign-order/<int:order_id>/<int:delivery_person_id>/', views.assign_order_to_delivery, name='assign_order'),
    path('update-location/<int:delivery_person_id>/', views.update_delivery_location, name='update_location'),
    path('track-order/<int:order_id>/', views.order_tracking_view, name='track_order'),
]
