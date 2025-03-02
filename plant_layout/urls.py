# plant_layout/urls.py
from django.urls import path
from . import views

app_name = 'plant_layout'  # Ensure app_name is defined

urlpatterns = [
    path('', views.plant_layout, name='plant_layout'),
    path('api/layouts/', views.get_all_layouts, name='get_all_layouts'),
    path('api/layouts/<int:layout_id>/', views.get_layout, name='get_layout'),  # Ensure this line is present
    path('api/layouts/save/', views.save_layout, name='save_layout'),
    path('api/layouts/<int:layout_id>/delete/', views.delete_layout, name='delete_layout'),
    path('api/plants/', views.plant_list, name='plant_list'),
   
    # Add these new URLs
    path('add-plant/', views.add_plant, name='add_plant'),
    path('plants/', views.plant_list_view, name='plant_list'),  # New view for plant list page
   
    path('upload-layout/', views.upload_layout, name='upload_layout'),
    path('save-plant-positions/<int:layout_id>/', views.save_plant_positions, name='save_plant_positions'),
    path('get-layout/<int:layout_id>/', views.get_layout, name='get_layout'),
]