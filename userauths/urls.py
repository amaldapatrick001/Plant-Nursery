from django.urls import path
from userauths import views

app_name = "userauth"

urlpatterns = [
    path('sign-up/', views.sign_up, name='sign_up'),  # Ensure the path matches the view name
]
