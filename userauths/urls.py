from django.urls import include, path
from .views import add_expert, adminindex, delete_user_view, delivery_dashboard, echange_password, password_reset_confirm, password_reset_request, register, login, logout, IndexView, register_delivery_personnel, undo_delete_view, update_expert_profile, update_profile, user_details, user_details_view, google_login, google_callback, assigned_orders, delivery_history, update_status

from django.views.generic import TemplateView 

app_name = "userauths"

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('index/', IndexView.as_view(), name='index'),
    path('adminindex/', adminindex.as_view(), name='adminindex'),
    path('password_reset/', password_reset_request, name='password_reset'),
    path('reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('password_reset/done/', TemplateView.as_view(template_name="userauths/password_reset_done.html"), name='password_reset_done'), 
    path('reset/done/', TemplateView.as_view(template_name="userauths/password_reset_complete.html"), name='password_reset_complete'),

    
    path('user-details/', user_details, name='user_details'),


    path('Del-restore/', user_details_view, name='user_details_view'),  # View for showing active and deleted users
    path('delete-user/<int:uid>/', delete_user_view, name='delete_user_view'),  # Soft delete user
    path('undo-delete/<int:uid>/', undo_delete_view, name='undo_delete_view'),  # Restore user
 path('profile/update/', update_profile, name='update_profile'),  # Add this line for the update_profile view
path('auth/', include('social_django.urls', namespace='social')),  # Social Auth URLs
    path('google/login', google_login, name='google_login'),
    path('google/callback', google_callback, name='google_callback'),

    path('admin/add_expert/', add_expert, name='add_expert'),
path('expert/update-profile/', update_expert_profile, name='update_expert_profile'),
    path('expert/echange-password/', echange_password, name='echange_password'),

     path('register_delivery_personnel/', register_delivery_personnel, name='register_delivery_personnel'),
#     path('delivery_personnel/update/<int:delivery_personnel_id>/', update_delivery_personnel, name='update_delivery_personnel'),
# path('delivery_personnel/', delivery_personnel_list, name='delivery_personnel_list'),
    path('delivery/dashboard/', delivery_dashboard, name='delivery_dashboard'),
    path('delivery/assigned-orders/', assigned_orders, name='assigned_orders'),
    path('delivery/history/', delivery_history, name='delivery_history'),
    path('delivery/update-status/', update_status, name='update_status'),
]