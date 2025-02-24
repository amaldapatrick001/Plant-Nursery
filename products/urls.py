from django.urls import path
from .views import (
    add_batch,
    add_category,
    add_product,
    add_to_wishlist,
    batch_list_view,
    category_list,
    category_update,
    cproduct_details,
    cproduct_list,
    edit_category,
    get_cultivation_methods,
    get_plant_category,
    load_plant_types,
    product_list,
    remove_from_wishlist,
    update_category_status,
    plant_type_list,
    add_plant_type,
    plant_type_update,
    update_plant_type_status,
    edit_plant_type,
    add_plant_category,
    plant_category_list,
    edit_plant_category,
    wishlist_addtocart,
    wishlist_view,
)

app_name = 'products'

urlpatterns = [
    # Category URLs
    path('categories/', category_list, name='category-list'),  # List active categories
    path('manage-categories/', category_update, name='category-update'),  # Manage categories
    path('add-category/', add_category, name='add-category'),  # Add a new category
    path('update-category-status/<int:category_id>/', update_category_status, name='update-category-status'),  # Toggle status
    path('edit-category/<int:category_id>/', edit_category, name='edit-category'),  # Edit category

    # Plant Type URLs
    path('plant-types/', plant_type_list, name='plant-type-list'),
    path('add-plant-type/', add_plant_type, name='add-plant-type'),
    path('manage-plant-types/', plant_type_update, name='plant-type-update'),
    path('update-plant-type-status/<int:plant_type_id>/', update_plant_type_status, name='update-plant-type-status'),
    path('edit-plant-type/<int:plant_type_id>/', edit_plant_type, name='edit-plant-type'),

    # Plant Category URLs
    path('plant-categories/', plant_category_list, name='plant-category-list'),
    path('add-plant-category/', add_plant_category, name='add-plant-category'),
    path('edit-plant-category/<int:category_id>/', edit_plant_category, name='edit-plant-category'),
    path('get-cultivation-methods/<int:category_id>/', get_cultivation_methods, name='get_cultivation_methods'),

    # Product URLs
    path('add-product/', add_product, name='add_product'),
    path('product-list/', product_list, name='product_list'),
    path('get-plant-categories/', get_plant_category, name='get_plant_category'),

    # Batch URLs
    path('add-batch/', add_batch, name='add_batch'),
    path('batches/', batch_list_view, name='batch_list'),

    # AJAX URLs
    path('ajax/load-plant-types/', load_plant_types, name='ajax_load_plant_types'),

    # Customer Product URLs
    path('cproducts/', cproduct_list, name='cproduct_list'),
    path('cproduct-details/<int:product_id>/', cproduct_details, name='cproduct_details'),

    # Wishlist URLs
    path('wishlist/', wishlist_view, name='wishlist'),
    path('wishlist/add/<int:batch_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:batch_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/add-to-cart/<int:batch_id>/', wishlist_addtocart, name='wishlist_addtocart'),
]