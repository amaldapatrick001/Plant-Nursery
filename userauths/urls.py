from django.urls import path
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

