from django.urls import path
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
