from django.urls import path
from .views import view_undelivered_orders, view_delivery_history
app_name = 'delivery' 
urlpatterns = [
    path('undelivered_orders/', view_undelivered_orders, name='view_undelivered_orders'),
    path('delivery_history/', view_delivery_history, name='view_delivery_history'),
]