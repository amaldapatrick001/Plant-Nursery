from django.urls import path

from .views import confirm_delivery,confirm_delivery_page, ddelivery_history, delivery_overview, dupdate_order_status, dview_assigned_orders, view_undelivered_orders, view_delivery_history
app_name = 'delivery' 
urlpatterns = [
    path('undelivered_orders/', view_undelivered_orders, name='view_undelivered_orders'),
    path('delivery_history/', view_delivery_history, name='view_delivery_history'),
    
       path('assigned_orders/', dview_assigned_orders, name='view_assigned_orders'),
    path('update_order_status/<int:order_id>/', dupdate_order_status, name='update_order_status'),
path('delivery/overview/', delivery_overview, name='delivery_overview'),

path('ddelivery/history/', ddelivery_history, name='ddelivery_history'),
 path("confirm_delivery/<int:order_id>/", confirm_delivery_page, name="confirm_delivery_page"),
    path("confirm_delivery/", confirm_delivery, name="confirm_delivery"),
]