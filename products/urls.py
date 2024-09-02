from django.urls import path
from .views import product_list, add_product, update_product

app_name = "products"
urlpatterns = [
    path('', product_list, name='product_list'),
    path('add/', add_product, name='add_product'),
    path('update/<int:pk>/', update_product, name='update_product'),
]
