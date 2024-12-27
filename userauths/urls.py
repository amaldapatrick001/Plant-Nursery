from django.urls import include, path
from .views import adminindex, delete_user_view, password_reset_confirm, password_reset_request, register, login, logout, IndexView, undo_delete_view, update_profile, user_details, user_details_view, google_login, google_callback
from django.contrib.auth import views 
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
]
