# products/urls.py

from django.urls import path
from .views import add_category, category_list, product_list, add_product, update_product, product_details

app_name = "products"
urlpatterns = [
    path('', product_list, name='product_list'),
    path('<int:id>/', product_details, name='product_details'),  # Ensure this matches the view name
    path('add/', add_product, name='add_product'),
    path('update/<int:pk>/', update_product, name='update_product'),
    path('add-category/', add_category, name='add_category'),
    path('categories/', category_list, name='category_list'),
]
