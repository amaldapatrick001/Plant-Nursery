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
    wishlist,
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
    path('plant_type_list/', plant_type_list, name='plant-type-list'),  # Ensure this matches
    path('add_plant_type/', add_plant_type, name='add-plant-type'),
    path('plant-types/', plant_type_list, name='plant-type-list'),  # List active plant types
    path('add-plant-type/', add_plant_type, name='add-plant-type'),  # Add a new plant type
    path('manage-plant-types/', plant_type_update, name='plant-type-update'),  # Manage plant types
    path('update-plant-type-status/<int:plant_type_id>/', update_plant_type_status, name='update-plant-type-status'),  # Toggle status
    path('edit-plant-type/<int:plant_type_id>/', edit_plant_type, name='edit-plant-type'),  # Edit plant type

    # Plant Category URLs
    path('add-plant-category/', add_plant_category, name='add_plant_category'),
    path('add-plant-category/', add_plant_category, name='add-plant-category'),  # This should match your template
   path('plant_category_list/', plant_category_list, name='plant_category_list'),
    path('get_cultivation_methods/<int:category_id>/', get_cultivation_methods, name='get_cultivation_methods'),
    path('plant-categories/', plant_category_list, name='plant-category-list'),  # List plant categories
    path('edit-plant-category/<int:category_id>/', edit_plant_category, name='edit-plant-category'),  # Edit plant category

    # AJAX URLs
path('add-product/', add_product, name='add_product'),  # URL to add a product
    path('get-plant-categories/', get_plant_category, name='get_plant_category'),  # AJAX URL to get plant categories
    path('get-plant-categories/', get_plant_category, name='get_plant_category'),

    path('product_list/', product_list, name='product_list'),  # Product list

    # Batch URLs
    path('add-batch/', add_batch, name='add_batch'),  # Add batch
    path('batches/', batch_list_view, name='batch_list'),  # List batches
# AJAX URLs
    path('ajax/load-plant-types/', load_plant_types, name='ajax_load_plant_types'),  # Ensure this URL is present
path('cproducts/', cproduct_list, name='cproduct_list'),
 path('cproduct_details/<int:product_id>/', cproduct_details, name='cproduct_details'),
 path('cproduct_details/<int:product_id>/', cproduct_details, name='cproduct_details'),




    path('', wishlist, name='wishlist'),  # Display wishlist
    path('add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),  # Add to wishlist
    path('remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),  # Remove from wishlist
]