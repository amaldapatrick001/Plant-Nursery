from django.urls import path
from .views import ddelivery_history, delivery_overview, dupdate_order_status, dview_assigned_orders, view_undelivered_orders, view_delivery_history
app_name = 'delivery' 
urlpatterns = [
    path('undelivered_orders/', view_undelivered_orders, name='view_undelivered_orders'),
    path('delivery_history/', view_delivery_history, name='view_delivery_history'),
    
       path('assigned_orders/', dview_assigned_orders, name='view_assigned_orders'),
    path('update_order_status/<int:order_id>/', dupdate_order_status, name='update_order_status'),
path('delivery/overview/', delivery_overview, name='delivery_overview'),

path('ddelivery/history/', ddelivery_history, name='ddelivery_history'),

]