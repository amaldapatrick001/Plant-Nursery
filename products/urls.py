# products/urls.py

from django.urls import path
from .views import (
    add_category,
    aproduct_list,
    category_list,
    delete_product,
    product_list,
    add_product,
    update_product,
    product_details,
    update_stocks
)

app_name = "products"

urlpatterns = [
    path('', product_list, name='product_list'),
    path('aproduct/', aproduct_list, name='aproduct_list'),
    path('<int:id>/', product_details, name='product_details'),
    path('add/', add_product, name='add_product'),
    path('update/<int:id>/', update_product, name='update_product'),
    path('update-stocks/', update_stocks, name='update_stocks'),
    path('delete/<int:id>/', delete_product, name='delete_product'),
    path('add-category/', add_category, name='add_category'),
    path('categories/', category_list, name='category_list'),
]
