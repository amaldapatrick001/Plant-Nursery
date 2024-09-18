from django.urls import path
<<<<<<< HEAD
from .views import adminindex, password_reset_confirm, password_reset_request, register, login, logout, IndexView
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
]

=======
from .views import register, login, home, logout
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView  # Your custom password reset view

app_name = "userauths"
urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('home/', home, name='home'),
    path('logout/', logout, name='logout'),

    # Password reset paths
    path('password_reset/', CustomPasswordResetView.as_view(
        email_template_name='userauths/password_reset_email.html',
        template_name='userauths/password_reset_form.html'
    ), name='password_reset'),

    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='userauths/password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='userauths/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='userauths/password_reset_complete.html'), name='password_reset_complete'),
]
>>>>>>> origin/main
